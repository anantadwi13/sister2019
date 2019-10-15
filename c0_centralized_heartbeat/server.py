from c0_centralized_heartbeat.FileServer import  *
from threading import Thread
import time
import Pyro4


class HeartbeatDaemon(Thread):
    def __init__(self, server_id, T):      # T stands for time units
        Thread.__init__(self)
        self.T = T
        self.server_id = server_id

    def run(self):
        uri = "PYRONAME:client@localhost:7777"

        client = Pyro4.Proxy(uri)

        seq_no = 0
        while(True):
            try:
                client.beat(self.server_id, seq_no)
                seq_no += 1
            except:
                pass
            time.sleep(self.T)


def start_with_ns():
    #name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    #gunakan URI untuk referensi name server yang akan digunakan
    #untuk mengecek service apa yang ada di ns, gunakan pyro4-nsc -n localhost -p 7777 list
    t_units = 0.5


    daemon = Pyro4.Daemon(host="localhost")
    x_FileServer = Pyro4.expose(FileServer)
    uri_fileserver = daemon.register(x_FileServer)
    print("URI file server : ", uri_fileserver)
    ns = Pyro4.locateNS("localhost", 7777)

    for i in range(1, 6):
        server_id = "server{0}".format(i)
        ns.register(server_id, uri_fileserver)
        heartbeat_service = HeartbeatDaemon(server_id, t_units)
        heartbeat_service.start()

    daemon.requestLoop()

if __name__ == '__main__':
    start_with_ns()
