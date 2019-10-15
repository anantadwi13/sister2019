import Pyro4
from threading import Thread
import time


UNAVAILABLE_MSG = "Server is not available! Reconnecting..."


class HeartbeatModel(object):
    def __init__(self, server_id, seq, last_update):
        self.server_id = server_id
        self.seq = seq
        self.last_update = last_update
        self.is_alive = False

    def update(self, seq, last_update):
        self.seq = seq
        self.last_update = last_update

    def update_status(self, T):
        if time.time() - self.last_update > 3 * T:
            self.is_alive = False   # Unavailable
        else:
            self.is_alive = True    # Available


class Heartbeat:
    servers = dict()

    def beat(self, server_id, seq_num):     # server_id must be a string
        if server_id in Heartbeat.servers and isinstance(Heartbeat.servers[server_id], HeartbeatModel):
            Heartbeat.servers[server_id].update(seq_num, int(time.time()))
        else:
            Heartbeat.servers[server_id] = HeartbeatModel(server_id, seq_num, int(time.time()))


class HeartbeatDaemon(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        daemon = Pyro4.Daemon(host="localhost")
        ns = Pyro4.locateNS("localhost", 7777)
        x_ClientDaemon = Pyro4.expose(Heartbeat)
        uri_fileserver = daemon.register(x_ClientDaemon)
        print("URI file server : ", uri_fileserver)
        ns.register("client", uri_fileserver)
        daemon.requestLoop()


class HeartbeatCheckerDaemon(Thread):
    def __init__(self, T):      # T stands for time units
        Thread.__init__(self)
        self.T = T

    def run(self):
        while(True):
            for server_id, server in Heartbeat.servers.items():
                server.update_status(self.T)
                # print(server.__dict__)
            time.sleep(0.1)


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
    heartbeat_service = HeartbeatDaemon()
    heartbeat_checker_service = HeartbeatCheckerDaemon(t_units)
    server_task = ServerTask(fserver, default_server_id)
    heartbeat_service.start()
    heartbeat_checker_service.start()

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
