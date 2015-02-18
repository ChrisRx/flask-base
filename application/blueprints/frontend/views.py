from flask import request, render_template, jsonify, Blueprint, current_app, \
    session, redirect, url_for, g, flash, abort
from flask_login import login_required
from flask_mail import Message

from sqlalchemy.exc import OperationalError

from ...errors import *
from ...ext import db, mail, apimanager
from ...utils import  roles_accepted, roles_required, auth_func, tokenizer

module = Blueprint("frontend", __name__, url_prefix="")


@module.route('/', methods=['GET', 'POST'])
@login_required
@roles_accepted('user')
def index():
    items = []
    return render_template('index.html',
        items=items
    )

@module.route('/search', methods=['GET', 'POST'])
@login_required
@roles_accepted('user')
def search():
    _items = []
    query = request.args.get('q', None)
    if not query:
        abort(404)
    return jsonify({'results': _items})
