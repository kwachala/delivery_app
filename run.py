from multiprocessing import Process
from delivery_app.restaurant import create_restaurant_app
from delivery_app.order import create_order_app

CREATE_APP_LIST = [create_restaurant_app, create_order_app]


def run_app(port, service):
    app = CREATE_APP_LIST[service]()
    app.run(port=port)


if __name__ == "__main__":
    processes = []

    ports = [[5001, 0], [5002, 1]]

    for port in ports:
        proc = Process(target=run_app, args=(port[0], port[1]))
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()
