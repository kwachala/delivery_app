from multiprocessing import Process
from delivery_app.restaurant import create_restaurant_app


def run_app(port):
    app = create_restaurant_app()
    app.run(port=port)


if __name__ == '__main__':
    processes = []

    ports = [5001]

    for port in ports:
        proc = Process(target=run_app, args=(port,))
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()
