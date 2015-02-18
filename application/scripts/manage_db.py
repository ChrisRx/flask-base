#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import csv
import json
import time
import datetime

from werkzeug import import_string
from flask_script import Manager, prompt_bool

from sqlalchemy.schema import CreateTable

from application import create_app
from application.blueprints.user.models import User, Role
from application.ext import db

app = create_app()
manager = Manager(app, usage="Perform database operations")

@manager.command
def create(bind=None):
    "Create all database tables"
    if not bind:
        bind_tables = "all"
    else:
        bind_tables = bind
    binds = app.config.get('SQLALCHEMY_BINDS').keys()
    if bind not in binds:
        print("That bind does not exist")
    question = "This will create '{0}' tables.  Are you sure you want to proceed?".format(bind_tables)
    if prompt_bool(question, default=False):
        db.create_all(bind=bind)

@manager.command
def drop():
    "Drop all database tables"
    db.drop_all()

@manager.command
def init():
    "Initialize database tables for roles/groups"
    db.drop_all(bind='users')
    db.create_all(bind='users')
    Role.create_roles(app.config['USER_ROLES'])

@manager.command
def clear(bind=None):
    "Clear user generated data from tables"
    if not bind:
        bind_tables = "all"
    binds = app.config.get('SQLALCHEMY_BINDS').keys()
    if bind not in binds:
        print("That bind does not exist")
    question = "Clearing this will drop and recreate '{0}' tables.  Are you sure you want to proceed?".format(bind_tables)
    if prompt_bool(question, default=False):
        db.drop_all(bind=bind)
        db.create_all(bind=bind)

if __name__ == '__main__':
    try:
        manager.run()
    except KeyboardInterrupt:
        sys.stdout.write("CTRL+C Pressed. Shutting down...\n")
        sys.exit(0)
