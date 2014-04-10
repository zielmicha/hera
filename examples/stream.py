import requests
import json
import socket

proxy = ('localhost', 10003)
host = 'http://localhost:8080/'

resp = requests.post(host + 'sandbox/', data={
    'owner': 'foouser',
    'timeout': 8,
    'memory': 128,
    'disk': 123
})
resp.raise_for_status()
resp = resp.json()
id = resp['id']
print(id)
resp = requests.post(host + 'sandbox/' + id + '/exec', data={
    'args': json.dumps(["/bin/busybox", "sh", "-c", "read foo; echo hello, $foo"]),
})
resp.raise_for_status()
id = resp.json()['stdout'].split('/')[-1]

sock = socket.socket()
sock.connect(proxy)
sock.sendall(('id=%s\n' % id).encode())
sock.sendall(b'Franklin turtle\n')
print(sock.recv(4096).decode())
