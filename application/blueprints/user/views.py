from flask import request, render_template, jsonify, Blueprint, current_app, \
    session, redirect, url_for, g, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from .forms import LoginForm
from .models import User, Role

from ...errors import *
from ...ext import apimanager
from ...utils import  roles_accepted, roles_required, auth_func

module = Blueprint("user", __name__, url_prefix="/user")

@module.route('/manage', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin')
def manage_users():
    users = User.query.json()
    roles = [{'id': role.id, 'name': role.name} for role in Role.query.all()]
    return render_template('users.html',
        users=users,
        roles=roles
    )

@module.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        if not form.password.data:
            flash("Password cannot be blank", "danger")
            return redirect(url_for('user.login', next=form.next.data))
        user, authenticated = User.authenticate(form.username.data,
            form.password.data)
        if user and authenticated:
            login_user(user)
            return form.redirect('frontend.index')
        else:
            flash("Authorization failed. Please try again.", "danger")
    return render_template('login.html', form=form)

@module.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You were logged out")
    return redirect(request.args.get('next') or '/')
