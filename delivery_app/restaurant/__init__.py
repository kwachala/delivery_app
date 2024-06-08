import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery


restaurant_app = Flask(__name__)
restaurant_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
restaurant_app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")

# restaurant_app.config['JWT_ALGORITHM'] = 'HS256'
restaurant_app.config.update(
    CELERY_BROKER_URL='pyamqp://guest:guest@rabbitmq:5672//',
    CELERY_RESULT_BACKEND='rpc://'
)

celery = make_celery(restaurant_app)
db = SQLAlchemy(restaurant_app)
jwt = JWTManager(restaurant_app)

from .models import Restaurant, Menu, MenuItem
from .routes import restaurant_bp

with restaurant_app.app_context():
    db.create_all()

restaurant_app.register_blueprint(restaurant_bp, url_prefix='/restaurant_api')
