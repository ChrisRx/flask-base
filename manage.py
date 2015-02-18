#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

import os
import sys
import logging
import atexit
import signal

# Place local lib path first in path lookup
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))

# The follow cleans up the exit code should we exit with SIGINT
def signal_handler():
    sys.stdout.write("\rCTRL+C Pressed. Shutting down...\n")
    sys.exit(0)

import gevent
gevent.signal(signal.SIGINT, signal_handler)

from flask_script import Manager
from flask_migrate import MigrateCommand

from application import create_app
from application.ext import db
from application.scripts.manage_db import manager as database_manager
from application.scripts.manage_service import manager as service_manager
from application.scripts.manage_users import manager as user_manager

try:
    app = create_app()
except FatalError as e:
    sys.stderr.write("{0}".format(e))

manager = Manager(app, with_default_commands=False)

manager.add_command("db", database_manager)
manager.add_command("service", service_manager)
manager.add_command("users", user_manager)
manager.add_command("migrate", MigrateCommand)

@manager.command
def server(reloader=False, debug=False, testing=False, port_other=None):
    if testing:
        from application.settings import Testing
        config = Testing
    elif debug:
        from application.settings import Development
        config = Development
    else:
        from application.settings import Production
        config = Production
    app = create_app(config=config)
    engine = db.get_engine(app, bind='users')
    for name, table in db.metadata.tables.items():
        if name in ['user', 'role', 'group']:
            if not table.exists(bind=engine):
                sys.stderr.write("User database not initialized.  Use ./manage.py db init\n")
                return
        if name in ['role', 'group']:
            if db.session.query(table).count() == 0:
                sys.stderr.write("Roles database not initialized.  Use ./manage.py db init\n")
                return
        if name in ['user']:
            if db.session.query(table).count() == 0:
                sys.stderr.write("Admin user not created.  Use ./manage.py users add <username>\n")
                return
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', None)
    if port_other is not None:
        port = int(port_other)
    if port is None:
        sys.stderr.write("You must set the port in application/settings.py or with '-p PORT'\n")
        sys.exit(1)
    def _runserver():
        import gevent.wsgi
        print(" * Starting on {0}:{1}".format(host, port))
        server = gevent.wsgi.WSGIServer((host, port), app)
        server.serve_forever()

    if reloader:
        from werkzeug.serving import run_with_reloader
        run_with_reloader(_runserver)
    else:
        _runserver()

if __name__ == '__main__':
    try:
        manager.run()
    except KeyboardInterrupt:
        sys.stdout.write("\rCTRL+C Pressed. Shutting down...\n")
        sys.exit(0)
