import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery
import logging
import threading


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery


deliveries_app = Flask(__name__)
deliveries_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
deliveries_app.config['JWT_SECRET_KEY'] = 'super-secret'
deliveries_app.config.update(
    CELERY_BROKER_URL='pyamqp://guest:guest@rabbitmq:5672//',
    CELERY_RESULT_BACKEND='rpc://'
)

celery = make_celery(deliveries_app)

db = SQLAlchemy(deliveries_app)
jwt = JWTManager(deliveries_app)

from .models import Restaurant, Menu, MenuItem
from .routes import deliveries_bp

with deliveries_app.app_context():
    db.create_all()

from kombu import Connection, Exchange, Queue

__all__ = ['celery']


@celery.task(queue='order_queue')
def process_order(order_data):
    print(f"Processing order: {order_data}")
    # Tu dodaj logikę przetwarzania zamówienia


def consume_orders():
    global x
    exchange = Exchange('orders', type='direct')
    queue = Queue('order_queue', exchange, routing_key='order')

    with Connection('pyamqp://guest:guest@rabbitmq:5672//') as conn:
        with conn.Consumer(queue, callbacks=[process_order_callback]) as consumer:
            while True:
                try:
                    conn.drain_events()
                except Exception as e:
                    continue  # Kontynuuj przetwarzanie kolejnych wiadomości


def process_order_callback(body, message):
    try:
        # Spróbuj przetworzyć wiadomość
        process_order.delay(body)
        message.ack()
    except (TypeError, ValueError, Exception) as e:
        message.reject()  # Odrzuć wiadomość, jeśli wystąpił błąd


deliveries_app.register_blueprint(deliveries_bp, url_prefix='/deliveries_api')

thread = threading.Thread(target=consume_orders)
thread.daemon = True  # wątek zakończy się po zamknięciu aplikacji
thread.start()
