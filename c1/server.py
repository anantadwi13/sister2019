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


def get_fileserver_object(nama_server):
    uri = "PYRONAME:{}@localhost:7777".format(nama_server)
    fserver = Pyro4.Proxy(uri)
    return fserver


def init_server():
    FileServer.DIR = ".\\{}\\".format(namainstance)
    FileServer.NAME = namainstance
    try:
        os.mkdir(FileServer.DIR)
    except:
        pass

    FileServer.FILEHISTORY = "{}{}".format(FileServer.DIR, FileServer.FILEHISTORY)
    print(FileServer.FILEHISTORY)
    with open(FileServer.FILEHISTORY, 'a+') as fw:
        pass
    with open(FileServer.FILEHISTORY, 'r') as fr:
        FileServer.HISTORY = {'timestamp': time, 'history': {}}
        try:
            FileServer.HISTORY = json.loads(fr.read())
        except Exception as e:
            print(e)
            pass

    # for failover
    curr_history = {'timestamp': 0, 'history': {}}
    selected_server = None
    for server in FileServer.SERVER:
        if server == FileServer.NAME: continue
        tmp_history = get_fileserver_object(server).get_file_history()
        if tmp_history is None or tmp_history['data'] is None or tmp_history['data']['timestamp'] <= curr_history['timestamp']: continue
        curr_history = tmp_history['data']
        selected_server = get_fileserver_object(server)

    if selected_server is not None:
        fs = FileServer()
        for filename, histories in curr_history['history'].items():
            for cmd in histories:
                if cmd == FileServer.CMD_CREATE:
                    fs.create(filename, False)
                elif cmd == FileServer.CMD_UPDATE:
                    fs.update(filename, selected_server.read(filename)['data'], False)
                elif cmd == FileServer.CMD_DELETE:
                    fs.delete(filename, False)


def start_with_ns():
    # name server harus di start dulu dengan  pyro4-ns -n localhost -p 7777
    # gunakan URI untuk referensi name server yang akan digunakan
    # untuk mengetahui instance apa saja yang aktif gunakan pyro4-nsc -n localhost -p 7777 list

    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS("localhost", 7777)
    ping_service = PingService()

    ping_service.start()
    insert_server()
    init_server()
    x_FileServer = Pyro4.expose(FileServer)
    uri_fileserver = daemon.register(x_FileServer)
    ns.register("{}".format(namainstance), uri_fileserver, metadata={"{}".format(namainstance)})
    # untuk instance yang berbeda, namailah fileserver dengan angka
    # ns.register("fileserver2", uri_fileserver)
    # ns.register("fileserver3", uri_fileserver)

    daemon.requestLoop()
    delete_server()

    ping_service.kill()


def insert_server():
    with open(SERVERINSTANCE_FILE, 'a+') as fw:
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
            time.sleep(100)

    def kill(self):
        self.running = False


if __name__ == '__main__':
    start_with_ns()
