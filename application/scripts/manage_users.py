#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
import signal

from flask_script import Manager, prompt, prompt_bool, prompt_choices, prompt_pass

from application import create_app
from application.ext import db

from application.blueprints.user.models import User, Role

app = create_app()
manager = Manager(app, with_default_commands=False, usage="Basic user management")

def add_user(username, password, first_name, last_name, email, roles=[], groups=[]):
        print("======================================\n")
        print("Username: {0}".format(username))
        print("First Name: {0}".format(first_name))
        print("Last Name: {0}".format(last_name))
        print("Email: {0}".format(email))
        print("Roles: {0}".format(",".join(roles)))
        if prompt_bool("Is this information correct?", default=True):
            User.create_user(username, password, first_name, last_name, email, roles)
            print("User {0} created".format(username))
        else:
            print("User {0} was not created".format(username))

def add_items(name, item_choices, default_item):
        items_added = []
        while len(item_choices) > 0:
            if not prompt_bool("Add {0}s?".format(name.lower()), default=True):
                break
            if default_item not in item_choices:
                default_item = item_choices[0]
            item = prompt_choices("{0}".format(name), choices=item_choices,
                default=default_item)
            print("Added {0}: {1}".format(name, item))
            items_added.append(item)
            item_choices.remove(item)
        return items_added

@manager.command
def add(username, password, first_name, last_name, email):
    try:
        if User.query.count() == 0:
            admin = prompt_bool("Currently there are no users, do you wish to create an admin?", default=True)
            if admin:
                add_user(username, password, first_name, last_name, email,
                    ['admin', 'user'])
                sys.exit(0)
        default_user = prompt_bool("Default user profile?", default=True)
        if default_user:
            add_user(username, password, first_name, last_name, email, ['user'])
            sys.exit(0)
        roles = add_items("Role", app.config.get('USER_ROLES', ['user']), 'user')
        add_user(username, password, first_name, last_name, email, roles)
        sys.exit(0)
    except KeyboardInterrupt:
        pass

@manager.command
def list():
    users = User.query.all()
    for user in users:
        print "%s %s (%s)" % (user.first_name, user.last_name, user.username)
        for role in user.roles:
            print "\t", role

@manager.command
def remove(username):
    username = username.lower()
    user = User.query.filter_by(username=username).first()
    if not user:
        print "Could not find user"
        return
    confirmed = prompt_bool("Are you sure you want to remove this user?", default=False)
    if confirmed:
        db.session.delete(user)
        db.session.commit()
        print "User %s removed" % username

if __name__ == '__main__':
    try:
        manager.run()
    except KeyboardInterrupt:
        sys.stdout.write("CTRL+C Pressed. Shutting down...\n")
        sys.exit(0)
