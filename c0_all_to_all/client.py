from c0_all_to_all.Heartbeat import *
import time


UNAVAILABLE_MSG = "Server is not available! Reconnecting..."


class ServerTask:
    def __init__(self, server, server_id):
        self.server = server
        self.server_id = server_id

    def is_available(self):
        if not self.server_id in Heartbeat.servers or not Heartbeat.servers[self.server_id].is_alive:
            return False
        return True

    def create(self, filename, content):
        if not self.is_available():
            return UNAVAILABLE_MSG
        else:
            self.server.create(filename, content)

    def read(self, filename):
        if not self.is_available():
            return UNAVAILABLE_MSG
        else:
            self.server.read(filename)

    def update(self, filename, content):
        if not self.is_available():
            return UNAVAILABLE_MSG
        else:
            self.server.update(filename, content)

    def delete(self, filename):
        if not self.is_available():
            return UNAVAILABLE_MSG
        else:
            self.server.delete(filename)

    def list(self, directory):
        if not self.is_available():
            return UNAVAILABLE_MSG
        else:
            return self.server.list(directory)


def test_with_ns():
    t_units = 0.5
    default_server_id = "server1"
    uri = "PYRONAME:{0}@localhost:7777".format(default_server_id)

    fserver = Pyro4.Proxy(uri)
    heartbeat_service = HeartbeatDaemon('client')
    heartbeat_checker_service = HeartbeatCheckerDaemon(t_units)
    server_task = ServerTask(fserver, default_server_id)
    heartbeat_service.start()
    heartbeat_checker_service.start()

    heartbeat_send_service = HeartbeatSendDaemon('client', '{0}_heartbeat'.format(default_server_id), t_units)
    heartbeat_send_service.start()

    time.sleep(1)

    run = True
    while(run):
        if not server_task.is_available():
            print(UNAVAILABLE_MSG)
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
