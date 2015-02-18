import os
import sys
import logging
import time
import datetime
import tempfile as _tempfile
import contextlib
import subprocess
import hashlib
import re
import multiprocessing
import json
import atexit
import collections
import base64
from functools import wraps

from werkzeug import import_string

from sqlalchemy import types as sqltypes

from flask import current_app
from flask import abort, g, session, url_for, request, redirect
from flask_login import current_user
from flask_principal import RoleNeed, Permission
from flask_restless import ProcessingException

from .ext import db

from webassets.filter import Filter
from webassets.exceptions import FilterError

import hmac
from passlib.context import CryptContext

def generate_encrypted_password(password):
    password_hash = get_hmac(password).decode('ascii')
    return encrypt_password(password_hash)

def encode_string(string):
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    return string

def get_hmac(password):
    salt = current_app.config.get("SECRET_KEY")
    h = hmac.new(encode_string(salt), encode_string(password), hashlib.sha512)
    return base64.b64encode(h.digest())

def encrypt_password(password):
    ctx = CryptContext(schemes=['sha512_crypt'])
    return ctx.encrypt(password)

def verify_password(password_hash, encrypted_password):
    ctx = CryptContext(schemes=['sha512_crypt'])
    return ctx.verify(password_hash, encrypted_password)


class RiotJS(Filter):
    name = 'riotjs'
    options= {
        'riotjs_bin': ('binary', 'riotjs_bin')
    }

    def open(self, out, source_path, **kw):
        output_path = kw.get('output_path')
        binary = self.riotjs_bin or 'riot'

        with tempfile(suffix='.js', delete=True) as output_file:
            if which(binary) is None:
                raise Exception("riotjs not installed.  install with 'npm install -g riot'")
            try:
                proc = subprocess.Popen([binary, source_path, output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=(os.name == 'nt')
                    )
            except OSError as error:
                if error.errno == 2:
                    raise Exception("riotjs not installed")
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                raise FilterError(("riotjs: subprocess error: {0}".format(stderr)))
            elif stderr:
                print("riotjs filter has warnings: {0}".format(stderr))
            with open(output_file, 'rb') as f:
                out.write(f.read().decode('utf-8'))

@contextlib.contextmanager
def tempfile(suffix='', prefix='tmp', dir=None, delete=True):
    fd, name = _tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        os.close(fd)
        yield name
    finally:
        if delete:
            try:
                os.remove(name)
            except OSError:
                pass

def auth_func(*args, **kw):
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not authenticated!', code=401)

alpha_numeric = re.compile('[^\w\s]')

def tokenizer(s):
    cleaned_string = alpha_numeric.sub('', s.strip())
    return cleaned_string.split(' ')

def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            user = g.user
            for role in user.roles:
                if role.name not in roles:
                    return abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def roles_accepted(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            user = g.user
            for role in user.roles:
                if role.name in roles:
                    return fn(*args, **kwargs)
            return abort(403)
        return decorated_view
    return wrapper

def apikey_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        key = request.args.get('api_key', None)
        if not key:
            return abort(403)
        current_key = current_app.config.get('API_KEY', None)
        print current_key
        if key != current_key:
            return abort(401)
        return fn(*args, **kwargs)
    return decorated_function

def check_api_auth(instance_id=None, **kwargs):
    key = request.args.get('api_key', None)
    if not key:
        return abort(403)
    current_key = current_app.config.get('API_KEY', None)
    if not (key == current_key):
        return abort(401)

def map_async(target, args=None):
    process = multiprocessing.Process(target=target, args=args)
    process.daemon = True
    process.start()

def run_command(cmd, data=None):
    try:
        print cmd
        process = subprocess.Popen(cmd,
            universal_newlines=True,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        out, err = process.communicate()
        rc = process.returncode
        return collections.namedtuple("Response",
            cmd=cmd,
            stdout=out,
            stderr=err,
            rc=rc
        )
    except Exception as exc:
        print("CommandError: {0}".format(exc))

def import_by_path(path):
    module_name, object_name = path.rsplit('.', 1)
    module = import_string(path)
    return module, object_name

def ensure_path_exists(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def ensure_file_exists(filepath):
    try:
        with open(filepath, 'rb'):
            pass
        return True
    except IOError:
        with open(filepath, 'a'):
            pass
        return False

def serialize_date(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None
