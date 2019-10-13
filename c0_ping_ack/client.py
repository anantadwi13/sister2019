import Pyro4
from threading import Thread
import time


class PingService(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server
        self.server_is_alive = False

    def run(self):
        while(True):
            try:
                if self.server.ping():
                    self.server_is_alive = True
                else:
                    self.server_is_alive = False
                # print("ok")
            except Exception as e:
                self.server_is_alive = False
                # print(e)


class ServerTask:
    def __init__(self, server, ping_service):
        self.server = server
        self.ping_service = ping_service

    def create(self, filename, content):
        if not self.ping_service.server_is_alive:
            return "Server is not available! Reconnecting..."
        else:
            self.server.create(filename, content)

    def read(self, filename):
        if not self.ping_service.server_is_alive:
            return "Server is not available! Reconnecting..."
        else:
            self.server.read(filename)

    def update(self, filename, content):
        if not self.ping_service.server_is_alive:
            return "Server is not available! Reconnecting..."
        else:
            self.server.update(filename, content)

    def delete(self, filename):
        if not self.ping_service.server_is_alive:
            return "Server is not available! Reconnecting..."
        else:
            self.server.delete(filename)

    def list(self, directory):
        if not self.ping_service.server_is_alive:
            return "Server is not available! Reconnecting..."
        else:
            return self.server.list(directory)


def test_with_ns():
    uri = "PYRONAME:fileserver@localhost:7777"
    fserver = Pyro4.Proxy(uri)
    ping_service = PingService(fserver)
    server_task = ServerTask(fserver, ping_service)
    ping_service.start()

    time.sleep(1)

    run = True
    while(run):
        if not ping_service.server_is_alive:
            print("Server is not available! Reconnecting...")
            time.sleep(1)
            continue

        type = input("\nCommands:\n\t1 to create file\n\t2 to read file\n\t3 to update file\n\t4 to delete file\n\t5 to show list files\n\t6 to exit\n> ")
        if type == "1":
            filename = input("Filename : ")
            text = input("Content : ")
            print(server_task.create(filename, text))
        elif type == "2":
            filename = input("Filename : ")
            print(server_task.read(filename))
        elif type == "3":
            filename = input("Filename : ")
            text = input("Content : ")
            print(server_task.update(filename, text))
        elif type == "4":
            filename = input("Filename : ")
            print(server_task.delete(filename))
        elif type == "5":
            directory = input("Directory : ")
            print(server_task.list(directory))
        elif type == "6":
            run = False
            print("Exiting!")
        else:
            print("Command not found!")


if __name__=='__main__':
    test_with_ns()
