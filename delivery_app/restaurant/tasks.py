# restaurant_service/tasks.py
from celery import Celery
from kombu import Connection, Exchange, Queue
from . import celery


@celery.task(queue='order_queue')
def send_order_to_queue(order_data):
    exchange = Exchange('orders', type='direct')
    queue = Queue('order_queue', exchange, routing_key='order')

    with Connection('pyamqp://guest:guest@rabbitmq:5672//') as conn:
        producer = conn.Producer()
        producer.publish(order_data, exchange=exchange, routing_key='order', declare=[queue])
