# Tutorial

## Instalasi

https://buildmedia.readthedocs.org/media/pdf/pyro4/stable/pyro4.pdf


Untuk aktifasi virtualenv
jika menggunakan ubuntu
install python3-venv
apt-get install python3-venv

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


menjalankan program
cd c0
python greet_server.py


untuk client
python greet_client.py

## Menjalankan di 2 Mesin Berbeda

1. Pastikan firewall terbuka untuk port server (7777)
2. Jalankan command berikut pada server
``` bash
pyro4-ns -n <ipserver> -p 7777
```
3. Ganti [line-17 dan line-18 file `greet_server.py`](https://github.com/anantadwi13/sister2019/blob/ef93f394efa59f149dcfd028d85ed85080a07d21/c0/greet_server.py#L17-L18) menjadi
``` python
daemon = Pyro4.Daemon(host="<ipserver>")
ns = Pyro4.locateNS("<ipserver>",7777)
```
4. Jalankan `greet_server.py` dan `greet_client.py`