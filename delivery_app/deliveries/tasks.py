import logging

from . import celery
from kombu import Connection, Exchange, Queue


@celery.task
def process_order(order_data):
    print(f"Processing order: {order_data}")
    # Tu dodaj logikę przetwarzania zamówienia


def consume_orders():
    exchange = Exchange('orders', type='direct')
    queue = Queue('order_queue', exchange, routing_key='order')

    with Connection('pyamqp://guest:guest@rabbitmq:5672//') as conn:
        with conn.Consumer(queue, callbacks=[process_order_callback], accept=['json']) as consumer:
            while True:
                logging.info("Waiting for messages")
                conn.drain_events()


def process_order_callback(body, message):
    process_order.delay(body)
    message.ack()
