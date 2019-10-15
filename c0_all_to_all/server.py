from c0_all_to_all.FileServer import *
from c0_all_to_all.Heartbeat import *
from threading import Thread
import time
import Pyro4


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

    server_id = "server1"
    ns.register(server_id, uri_fileserver)
    heartbeat_send_service = HeartbeatSendDaemon(server_id, 'client', t_units)
    heartbeat_send_service.start()

    heartbeat_service = HeartbeatDaemon('{0}_heartbeat'.format(server_id))
    heartbeat_service.start()
    heartbeat_checker_service = HeartbeatCheckerDaemon(t_units)
    heartbeat_checker_service.start()

    daemon.requestLoop()

if __name__ == '__main__':
    start_with_ns()
