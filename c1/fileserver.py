import os
import base64
import Pyro4
import json
import time


class FileServer(object):
    FILEHISTORY = ".history"
    CMD_CREATE = 1
    CMD_UPDATE = 2
    CMD_DELETE = 3

    HISTORY = {}
    NAME = ""
    DIR = ""
    SERVER = []

    def __init__(self):
        pass

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

    def file_history(self, filename=None, cmd=0):
        if filename is None or cmd <= 0: return

        if filename in FileServer.HISTORY['history']:
            if cmd == FileServer.CMD_CREATE:
                FileServer.HISTORY['history'][filename].append(cmd)
            elif cmd == FileServer.CMD_UPDATE:
                FileServer.HISTORY['history'][filename].clear()
                FileServer.HISTORY['history'][filename].append(FileServer.CMD_CREATE)
                FileServer.HISTORY['history'][filename].append(cmd)
            elif cmd == FileServer.CMD_DELETE:
                FileServer.HISTORY['history'][filename].clear()
                FileServer.HISTORY['history'][filename].append(cmd)
        else:
            FileServer.HISTORY['history'][filename] = [cmd]
        FileServer.HISTORY['timestamp'] = time.time()
        with open(FileServer.FILEHISTORY, 'w+') as fw:
            fw.write(json.dumps(FileServer.HISTORY))

    def get_file_history(self):
        return self.create_return_message('200', 'OK', FileServer.HISTORY)

    def create_return_message(self, kode='000', message='kosong', data=None):
        return dict(kode=kode, message=message, data=data)

    def list(self):
        print(FileServer.DIR)
        print("list ops")
        try:
            daftarfile = []
            for x in os.listdir(FileServer.DIR):
                if '.history' not in x:
                    daftarfile.append(x)
            return self.create_return_message('200', daftarfile)
        except:
            return self.create_return_message('500', 'Error')

    def create(self, nama='filename000', sync=True):
        print("create ops {}".format(nama))
        try:
            self.file_history(nama, FileServer.CMD_CREATE)
            if os.path.exists("{}{}".format(FileServer.DIR, nama)):
                return self.create_return_message('102', 'OK', 'File Exists')
            f = open("{}{}".format(FileServer.DIR, nama), 'wb', buffering=0)
            f.close()
            if sync:
                self.synchronize(FileServer.CMD_CREATE, {"nama": nama, "sync": False})
            return self.create_return_message('100', 'OK')
        except:
            return self.create_return_message('500', 'Error')

    def read(self, nama='filename000'):
        print("read ops {}".format(nama))
        try:
            f = open("{}{}".format(FileServer.DIR, nama), 'r+b')
            contents = f.read().decode()
            f.close()
            return self.create_return_message('101', 'OK', contents)
        except:
            return self.create_return_message('500', 'Error')

    def update(self, nama='filename000', content='', sync=True):
        print("update ops {}".format(nama))

        if (str(type(content)) == "<class 'dict'>"):
            content = content['data']
        try:
            f = open("{}{}".format(FileServer.DIR, nama), 'w+b')
            f.write(content.encode())
            f.close()
            self.file_history(nama, FileServer.CMD_UPDATE)
            if sync:
                self.synchronize(FileServer.CMD_UPDATE, {"nama": nama, "content": content, "sync": False})
            return self.create_return_message('101', 'OK')
        except Exception as e:
            return self.create_return_message('500', 'Error', str(e))

    def delete(self, nama='filename000', sync=True):
        print("delete ops {}".format(nama))

        try:
            os.remove("{}{}".format(FileServer.DIR, nama))
            self.file_history(nama, FileServer.CMD_DELETE)
            if sync:
                self.synchronize(FileServer.CMD_DELETE, {"nama": nama, "sync": False})
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
