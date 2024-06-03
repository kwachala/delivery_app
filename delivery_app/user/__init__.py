import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .models import Restaurant, Menu, MenuItem
from .routes import user_bp

user_app = Flask(__name__)
user_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
user_app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")

# user_app.config['JWT_ALGORITHM'] = 'HS256'

db2 = SQLAlchemy(user_app)
jwt = JWTManager(user_app)

with user_app.app_context():
    db2.create_all()

user_app.register_blueprint(user_bp, url_prefix='/user_api')
