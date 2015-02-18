from flask_restless import APIManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_principal import Principal
from flask_sqlalchemy import SQLAlchemy

__all__ = ['apimanager', 'db', 'login_manager', 'mail']

apimanager = APIManager()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
