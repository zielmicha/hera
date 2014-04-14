import requests
import json
import socket
import select
import os
import atexit

proxy = ('localhost', 10003)
host = 'http://localhost:8080/'

resp = requests.post(host + 'sandbox/', data={
    'owner': 'foouser',
    'timeout': 120,
    'memory': 128,
    'disk': os.environ.get('template', 'new,5G'),
})
resp.raise_for_status()
resp = resp.json()
vm_id = resp['id']

def kill():
    resp = requests.post(host + 'sandbox/' + vm_id + '/kill')
    print('killed:', resp.json())

atexit.register(kill)

resp = requests.post(host + 'sandbox/' + vm_id + '/exec', data={
    'args': json.dumps(["/bin/busybox", "sh", "-i"]),
})
resp.raise_for_status()
id = resp.json()['stdout'].split('/')[-1]

sock = socket.socket()
sock.connect(proxy)
sock.sendall(('id=%s\n' % id).encode())
file = sock.makefile('rwb', 0)

infile = os.fdopen(0, 'rb', 0)
outfile = os.fdopen(1, 'wb', 0)

mapping = {
    infile: file,
    file: outfile
}

while True:
    R, W, E = select.select([file, infile],
                            [],
                            [file, infile])
    if E:
        break

    for r in R:
        mapping[r].write(r.read(1))
