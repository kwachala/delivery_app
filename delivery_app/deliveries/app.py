from . import deliveries_app, tasks


if __name__ == '__main__':
    import threading

    # Start the consumer in a separate thread
    consumer_thread = threading.Thread(target=tasks.consume_orders)
    consumer_thread.daemon = True
    consumer_thread.start()

    deliveries_app.run(debug=True)
