import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

user_app = Flask(__name__)
user_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
user_app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")

# user_app.config['JWT_ALGORITHM'] = 'HS256'

user_db = SQLAlchemy(user_app)
flask_bcrypt = Bcrypt(user_app)
jwt = JWTManager(user_app)

from .models import User
from .routes import user_bp

with user_app.app_context():
    user_db.create_all()

user_app.register_blueprint(user_bp, url_prefix='/user_api')
