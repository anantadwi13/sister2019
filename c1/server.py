from fileserver import *
import Pyro4
import sys
import threading
import json

SERVERINSTANCE_FILE = "server_instance"
namainstance = sys.argv[1] if len(sys.argv) >= 2 else "fileserver"


def start_without_ns():
    daemon = Pyro4.Daemon()
    x_FileServer = Pyro4.expose(FileServer)
    uri = daemon.register(x_FileServer)
    print("my URI : ", uri)
    daemon.requestLoop()


def start_with_ns():
    # name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    # gunakan URI untuk referensi name server yang akan digunakan
    # untuk mengetahui instance apa saja yang aktif gunakan pyro4-nsc -n localhost -p 7777 list

    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 7777)
    FileServer.DIR = ".\\{}\\".format(namainstance)
    FileServer.NAME = namainstance
    x_FileServer = Pyro4.expose(FileServer)
    uri_fileserver = daemon.register(x_FileServer)
    ns.register("{}".format(namainstance), uri_fileserver, metadata={"{}".format(namainstance)})
    # untuk instance yang berbeda, namailah fileserver dengan angka
    # ns.register("fileserver2", uri_fileserver)
    # ns.register("fileserver3", uri_fileserver)

    ping_service = PingService()

    insert_server()
    ping_service.start()
    daemon.requestLoop()
    delete_server()

    ping_service.kill()


def insert_server():
    with open(SERVERINSTANCE_FILE, 'w') as fw:
        pass
    with open(SERVERINSTANCE_FILE, 'r') as fr:
        servers = []
        try:
            servers: list = json.loads(fr.read())
        except:
            pass
        try:
            if not namainstance in servers:
                servers.append(namainstance)
                with open(SERVERINSTANCE_FILE, 'w') as fw:
                    fw.write(json.dumps(servers))
        except Exception as e:
            print(e)


def delete_server():
    with open(SERVERINSTANCE_FILE, 'r') as fr:
        try:
            servers: list = json.loads(fr.read())
            servers.remove(namainstance)
            with open(SERVERINSTANCE_FILE, 'w') as fw:
                fw.write(json.dumps(servers))
        except Exception as e:
            print(e)


class PingService(threading.Thread):
    def __init__(self):
        self.running = True
        threading.Thread.__init__(self)

    def run(self) -> None:
        while self.running:
            with open(SERVERINSTANCE_FILE, 'r') as f:
                try:
                    servers = json.loads(f.read())
                    FileServer.SERVER.clear()
                    FileServer.SERVER.extend(servers)
                except:
                    pass

    def kill(self):
        self.running = False


if __name__ == '__main__':
    start_with_ns()
