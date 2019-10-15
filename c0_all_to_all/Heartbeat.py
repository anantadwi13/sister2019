from threading import Thread
import time
import Pyro4


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
    def __init__(self, ns_host):
        Thread.__init__(self)
        self.ns_host = ns_host

    def run(self):
        daemon = Pyro4.Daemon(host="localhost")
        ns = Pyro4.locateNS("localhost", 7777)
        x_ClientDaemon = Pyro4.expose(Heartbeat)
        uri_fileserver = daemon.register(x_ClientDaemon)
        print("URI file server : ", uri_fileserver)
        ns.register(self.ns_host, uri_fileserver)
        daemon.requestLoop()


class HeartbeatCheckerDaemon(Thread):
    def __init__(self, T):      # T stands for time units
        Thread.__init__(self)
        self.T = T

    def run(self):
        while(True):
            for server_id, server in Heartbeat.servers.items():
                server.update_status(self.T)
                print(server.__dict__)
            time.sleep(1)


class HeartbeatSendDaemon(Thread):
    def __init__(self, src_server, dest_server, T):      # T stands for time units
        Thread.__init__(self)
        self.T = T
        self.server_id = src_server
        self.dest_server = dest_server

    def run(self):
        uri = "PYRONAME:{0}@localhost:7777".format(self.dest_server)

        client = Pyro4.Proxy(uri)

        seq_no = 0
        while(True):
            try:
                client.beat(self.server_id, seq_no)
                seq_no += 1
            except:
                pass
            time.sleep(self.T)