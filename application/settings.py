from os import getcwd
from os.path import join, dirname, abspath, expanduser

class DefaultConfig(object):
    APP_TITLE = "Application Name"
    DEBUG = False
    TESTING = False
    HOST = "localhost"
    PORT = None
    SESSION_TIMEOUT = 600

class BaseConfig(DefaultConfig):
    HOME_DIR = expanduser('~')
    ROOT_DIR = getcwd()
    APP_DIR = dirname(abspath(__file__))
    DATA_DIR = join(APP_DIR, 'data')
    LOG_DIR = join(APP_DIR, 'logs/')

    SECRET_KEY = "11605eeb78cb7e1396e9a21b74371b06"

    # Blueprints
    APP_BLUEPRINTS = [
        'application.blueprints.frontend',
        'application.blueprints.user',
    ]

    # APIS
    APP_APIS = [
        {
            'path': 'user.models.User',
            'exclude_columns': [
                'allow_login',
                'roles.date_added',
            ]
        },
    ]

    # DB
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(join(DATA_DIR, 'data.db'))
    SQLALCHEMY_BINDS = {
        'users': 'sqlite:///{0}'.format(join(DATA_DIR, 'users.db')),
        'tests': 'sqlite:///{0}'.format(join(DATA_DIR, 'tests.db'))
    }

    # Admin
    ADMIN_EMAIL = ''

    # User
    USER_ROLES = [
        'admin',
        'user',
    ]

    # Flask-Login configuration for testing
    LOGIN_DISABLED = False

    # Email
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25

    # Logging
    ERROR_LOG = join(LOG_DIR, 'error.log')
    DEBUG_LOG = join(LOG_DIR, 'debug.log')

    SVC_PID_FILE = join(ROOT_DIR, 'test.pid')

class Development(BaseConfig):
    DEBUG = True

class Testing(BaseConfig):
    TESTING = True

class Production(BaseConfig):
    PORT = 5000
