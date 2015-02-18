import datetime

from ...database import db, Model
from ...ext import apimanager
from ...utils import serialize_date, generate_encrypted_password, get_hmac, \
    verify_password

roles = db.Table('roles',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    info={'bind_key': 'users'}
)

class User(Model):
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(65))
    last_name = db.Column(db.String(65))
    email = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    allow_login = db.Column(db.Boolean, default=True)

    roles = db.relationship('Role', secondary=roles,
        backref=db.backref('users', lazy='dynamic'))

    @classmethod
    def create_user(cls, username, password, first_name, last_name, email,
            roles=['user'], allow_login=True):
        username = username.lower()
        user = cls.query.filter(User.username==username).first()
        if user:
            print("User {0} already exists".format(username))
            return False
        else:
            new_user = User(
                username=username,
                password=generate_encrypted_password(password),
                first_name=first_name,
                last_name=last_name,
                email=email,
                allow_login=allow_login
            )
            db.session.add(new_user)
            new_roles = [role for role in Role.query.all() if role.name in \
                roles]
            for role in new_roles:
                new_user.roles.append(role)
            db.session.commit()
            return new_user

    @classmethod
    def authenticate(cls, username, password):
        if password is None:
            return False
        username = username.lower()
        user = cls.query.filter(User.username==username).first()
        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False
        return user, authenticated

    def check_password(self, password):
        password_hash = get_hmac(password).decode('ascii')
        if verify_password(password_hash, self.password):
            return True
        return False

    def toggle_login(self):
        if self.allow_login:
            self.allow_login = False
        else:
            self.allow_login = True
        db.session.commit()
        return self.allow_login

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    @property
    def is_admin(self):
        for role in self.roles:
            if role.name in ['administrator', 'admin']:
                return True
        return False

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def json(self):
        """Override json property method of Model to include roles and groups"""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'date_added': serialize_date(self.date_added),
            'roles': [{'id': role.id, 'name': role.name} for role in self.roles],
            'allow_login': self.allow_login
        }

class Role(Model):
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(65), unique=True)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def create_roles(cls, roles):
        for role in roles:
            role_exists = cls.query.filter(Role.name==role).first()
            if not role_exists:
                new_role = Role(name=role)
                db.session.add(new_role)
        db.session.commit()

    def __repr__(self):
        return "<Role '{0}'>".format(self.name)
