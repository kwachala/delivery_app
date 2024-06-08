from flask_sqlalchemy import SQLAlchemy
import enum
from sqlalchemy import Enum
from sqlalchemy.ext.hybrid import hybrid_property
from . import user_db, flask_bcrypt
from .utils import admin_required, hash_password, check_password_hash


class RoleEnum(enum.Enum):
    ADMIN = 'ADMIN'
    CUSTOMER = 'CUSTOMER'
    DELIVERER = 'DELIVERER'
    RESTAURANT = 'RESTAURANT'


class User(user_db.Model):
    __tablename__ = 'users'
    id = user_db.Column(user_db.Integer, primary_key=True)
    username = user_db.Column(user_db.String(255), unique=True, nullable=False)
    _password = user_db.Column('password', user_db.String(60), nullable=False)
    role = user_db.Column(Enum(RoleEnum), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = flask_bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self._password, password)
