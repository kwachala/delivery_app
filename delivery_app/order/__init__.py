import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.conf.update(app.config)
    return celery


order_app = Flask(__name__)
order_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
order_app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
order_app.config["PAYU_POS_ID"] = os.getenv("PAYU_POS_ID")
order_app.config["PAYU_CLIENT_ID"] = os.getenv("PAYU_CLIENT_ID")
order_app.config["PAYU_CLIENT_SECRET"] = os.getenv("PAYU_CLIENT_SECRET")

# restaurant_app.config['JWT_ALGORITHM'] = 'HS256'
order_app.config.update(
    CELERY_BROKER_URL="pyamqp://guest:guest@rabbitmq:5672//",
    CELERY_RESULT_BACKEND="rpc://",
)

celery = make_celery(order_app)
db = SQLAlchemy(order_app)
jwt = JWTManager(order_app)

from .models import Order, OrderItem
from .routes import order_bp

with order_app.app_context():
    db.create_all()

order_app.register_blueprint(order_bp, url_prefix="/order_api")
