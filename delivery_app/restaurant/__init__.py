import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

restaurant_app = Flask(__name__)
restaurant_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
restaurant_app.config["JWT_SECRET_KEY"] = "super-secret"

db = SQLAlchemy(restaurant_app)
jwt = JWTManager(restaurant_app)

from .models import Restaurant, Menu, MenuItem
from .routes import restaurant_bp

with restaurant_app.app_context():
    db.create_all()

restaurant_app.register_blueprint(restaurant_bp, url_prefix="/restaurant_api")
