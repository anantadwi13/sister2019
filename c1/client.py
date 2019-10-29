import Pyro4
import base64
import json

def get_fileserver_object():
    uri = "PYRONAME:fileserver@localhost:7777"
    fserver = Pyro4.Proxy(uri)
    return fserver

if __name__=='__main__':
    f = get_fileserver_object()
    f.create('slide1.pdf')
    f.update('slide1.pdf', content = open('slide1.pdf','rb+').read() )
    print(f.list())
    d = f.read('slide1.pdf')
    #kembalikan ke bentuk semula ke dalam file name slide1-kembali.pdf
    open('slide1-kembali.pdf','w+b').write(base64.b64decode(d['data']))

