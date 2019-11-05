import os
import base64
import Pyro4


class FileServer(object):
    CMD_CREATE = 1
    CMD_UPDATE = 2
    CMD_DELETE = 3

    NAME = ""
    DIR = ""
    SERVER = []

    def __init__(self):
        try:
            os.mkdir(FileServer.DIR)
        except:
            pass
        pass

    def get_fileserver_object(self, nama_server):
        uri = "PYRONAME:{}@localhost:7777".format(nama_server)
        fserver = Pyro4.Proxy(uri)
        return fserver

    def synchronize(self, cmd=0, data=None):
        if data is None:
            return
        for server in FileServer.SERVER:
            if server == FileServer.NAME:
                continue
            uri = "PYRONAME:{}@localhost:7777".format(server)
            fserver = Pyro4.Proxy(uri)
            if cmd == FileServer.CMD_CREATE:
                fserver.create(**data)
            elif cmd == FileServer.CMD_DELETE:
                fserver.delete(**data)
            elif cmd == FileServer.CMD_UPDATE:
                fserver.update(**data)

    def create_return_message(self, kode='000', message='kosong', data=None):
        return dict(kode=kode, message=message, data=data)

    def list(self):
        print(FileServer.DIR)
        print("list ops")
        try:
            daftarfile = []
            for x in os.listdir(FileServer.DIR):
                if 'FFF-' in x:
                    daftarfile.append(x[4:])
            return self.create_return_message('200', daftarfile)
        except:
            return self.create_return_message('500', 'Error')

    def create(self, name='filename000', sync=True):
        nama = 'FFF-{}'.format(name)
        print("create ops {}".format(nama))
        try:
            if os.path.exists("{}{}".format(FileServer.DIR, nama)):
                return self.create_return_message('102', 'OK', 'File Exists')
            f = open("{}{}".format(FileServer.DIR, nama), 'wb', buffering=0)
            f.close()
            if sync:
                self.synchronize(FileServer.CMD_CREATE, {"name": name, "sync": False})
            return self.create_return_message('100', 'OK')
        except:
            return self.create_return_message('500', 'Error')

    def read(self, name='filename000'):
        nama = 'FFF-{}'.format(name)
        print("read ops {}".format(nama))
        try:
            f = open("{}{}".format(FileServer.DIR, nama), 'r+b')
            contents = f.read().decode()
            f.close()
            return self.create_return_message('101', 'OK', contents)
        except:
            return self.create_return_message('500', 'Error')

    def update(self, name='filename000', content='', sync=True):
        nama = 'FFF-{}'.format(name)
        print("update ops {}".format(nama))

        if (str(type(content)) == "<class 'dict'>"):
            content = content['data']
        try:
            f = open("{}{}".format(FileServer.DIR, nama), 'w+b')
            f.write(content.encode())
            f.close()
            if sync:
                self.synchronize(FileServer.CMD_UPDATE, {"name": name, "content": content, "sync": False})
            return self.create_return_message('101', 'OK')
        except Exception as e:
            return self.create_return_message('500', 'Error', str(e))

    def delete(self, name='filename000', sync=True):
        nama = 'FFF-{}'.format(name)
        print("delete ops {}".format(nama))

        try:
            os.remove("{}{}".format(FileServer.DIR, nama))
            if sync:
                self.synchronize(FileServer.CMD_DELETE, {"name": name, "sync": False})
            return self.create_return_message('101', 'OK')
        except:
            return self.create_return_message('500', 'Error')


if __name__ == '__main__':
    k = FileServer()
    print(k.create('f1'))
    print(k.update('f1', content='wedusku'))
    print(k.read('f1'))
    #    print(k.create('f2'))
    #    print(k.update('f2',content='wedusmu'))
    #    print(k.read('f2'))
    print(k.list())
    # print(k.delete('f1'))
