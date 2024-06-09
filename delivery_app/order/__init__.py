import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

order_app = Flask(__name__)
order_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
order_app.config["JWT_SECRET_KEY"] = "super-secret"

db = SQLAlchemy(order_app)
jwt = JWTManager(order_app)

from .models import Order, OrderItem
from .routes import order_bp

with order_app.app_context():
    db.create_all()

order_app.register_blueprint(order_bp, url_prefix="/order_api")
