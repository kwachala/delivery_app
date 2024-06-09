import json
import os
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery
import logging
import threading

app = Celery('tasks', broker='pyamqp://guest:guest@rabbitmq:5672//')

deliveries_app = Flask(__name__)
deliveries_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
deliveries_app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")
deliveries_app.config.update(
    CELERY_BROKER_URL='pyamqp://guest:guest@rabbitmq:5672//',
    CELERY_RESULT_BACKEND='rpc://'
)

db = SQLAlchemy(deliveries_app)
jwt = JWTManager(deliveries_app)

from .models import Restaurant, Menu, MenuItem, Delivery
from .routes import deliveries_bp

with deliveries_app.app_context():
    db.create_all()

from kombu import Connection, Exchange, Queue


@app.task
def process_order(order_data):
    logging.info(f"Processing order: {order_data}")
    headers = {'Content-Type': 'application/json'}

    requests.post('http://127.0.0.1:5002/deliveries_api/add_delivery', data=json.dumps(order_data), headers=headers)


def consume_orders():
    global x
    exchange = Exchange('orders', type='direct')
    queue = Queue('orders_queue', exchange, routing_key='orders')

    with Connection('pyamqp://guest:guest@rabbitmq:5672//') as conn:
        with conn.Consumer(queue, callbacks=[process_order_callback]) as consumer:
            while True:
                try:
                    conn.drain_events()
                except Exception as e:
                    continue


def process_order_callback(body, message):
    process_order(json.loads(body))
    message.ack()


deliveries_app.register_blueprint(deliveries_bp, url_prefix='/deliveries_api')

thread = threading.Thread(target=consume_orders)
thread.daemon = True
thread.start()
