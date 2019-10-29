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
    f.create('slide2.pptx')
    f.update('slide1.pdf', content = base64.b64encode(open('slide1.pdf','rb+').read()) )
    f.update('slide2.pptx', content = base64.b64encode(open('slide2.pptx','rb+').read()) )
    print(f.list())
    print(f.read('slide1.pdf'))
    #kembalikan ke bentuk semula
    open('slide1-kembali.pdf','w+b').write(base64.b64decode(f.read('slide1.pdf')['data']).encode())

