import os
import logging
from datetime import timedelta
import webassets
from flask import Flask, g, session, request, current_app, abort, Blueprint, \
    render_template
from flask_login import current_user
from flask_principal import identity_loaded, Permission, RoleNeed, \
     UserNeed

from .assets import assets
from .blueprints.user.models import User
from .errors import StartupError
from .ext import *
from .utils import  import_by_path, ensure_path_exists, auth_func

def create_app(config=None):
    app = Flask(__name__)
    if not config:
        from .settings import Development
        config = Development
    app.config.from_object(config)
    session_timeout = app.config.get('SESSION_TIMEOUT', 60)
    app.permanent_session_lifetime = timedelta(minutes=session_timeout)
    configure_extensions(app)
    configure_blueprints(app)
    configure_logging(app)
    configure_error_handlers(app)
    return app

def configure_extensions(app):
    db.init_app(app)
    mail.init_app(app)
    assets.init_app(app)

    # Configure APIs the easy way
    apimanager.init_app(app, flask_sqlalchemy_db=db)
    apis = app.config.get('APP_APIS', [])
    for api in apis:
        model, model_name = import_by_path("application.blueprints.{0}".format(api.get('path', None)))
        methods = api.get('methods', ['GET', 'POST', 'PUT', 'DELETE'])
        results_per_page = api.get('results_per_page', 0)
        preprocessors = api.get('preprocessors', [auth_func])
        exclude_columns = api.get('exclude_columns', None)
        apimanager.create_api(model,
            methods=methods,
            results_per_page=results_per_page,
            preprocessors={
                'GET_SINGLE': preprocessors,
                'GET_MANY': preprocessors,
                'PUT_SINGLE': preprocessors,
                'PUT_MANY': preprocessors,
                'POST': preprocessors,
                'DELETE': preprocessors,
            },
            exclude_columns=exclude_columns
        )

    login_manager.init_app(app)
    login_manager.login_view = "user.login"

    @app.before_request
    def set_user():
        g.user = current_user

def configure_blueprints(app):
    blueprints = app.config.get('APP_BLUEPRINTS', [])
    for blueprint_path in blueprints:
        module, blueprint_name = import_by_path("{0}.views.module".format(blueprint_path))
        if isinstance(module, Blueprint):
            app.register_blueprint(module)
        else:
            raise StartupError("Unable to register blueprint %s at path %s" % (blueprint_name, blueprint_path))

def configure_logging(app):
    debug_log_file = app.config.get('DEBUG_LOG', None)
    if debug_log_file:
        ensure_path_exists(debug_log_file)
        debug_log_file_handler = logging.FileHandler(debug_log_file)
        debug_log_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        debug_log_file_handler.setLevel(logging.INFO)
        debug_log_file_handler.setFormatter(debug_log_file_formatter)
        app.logger.addHandler(debug_log_file_handler)
    error_log_file = app.config.get('ERROR_LOG', None)
    if error_log_file:
        ensure_path_exists(error_log_file)
        error_log_file_handler = logging.FileHandler(error_log_file)
        error_log_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_log_file_handler.setLevel(logging.ERROR)
        error_log_file_handler.setFormatter(error_log_file_formatter)
        app.logger.addHandler(error_log_file_handler)

@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).get(userid)

def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("500.html"), 500
