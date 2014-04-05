import uuid
import subprocess
import os
import traceback
import socket
import logging
import time
import threading
import json

from hera import vmcontroller
from hera import accounting

def spawn(request):
    sock = socket.socket()
    sock.bind(('0.0.0.0', 0))
    sock.listen(1)

    port = sock.getsockname()[1]
    secret = str(uuid.uuid4())

    logging.info('Spawning VM with config %r on port %d', request, port)
    if os.fork() == 0:
        try:
            loop(owner=request['owner'],
                 stats=request['stats'],
                 res_id=request['res_id'],
                 secret=secret,
                 sock=sock)
        except:
            traceback.print_exc()
        finally:
            os._exit(1)
    else:
        sock.close()
        return [socket.getfqdn(), port, secret]

def loop(owner, stats, res_id, secret, sock):
    vm = vm_init(stats, res_id)
    vm_server_loop(vm, secret, sock)

def vm_init(stats, res_id):
    last_heartbeat = [time.time()]

    def heartbeat_callback():
        accounting.derivative_resource_used(res_id)

    vm = vmcontroller.VM(heartbeat_callback=heartbeat_callback)
    vm.start(
        memory=stats['memory'])
    return vm

def vm_server_loop(vm, secret, sock):
    while True:
        client_sock, addr = sock.accept()
        threading.Thread(target=vm_loop,
                         args=[vm, secret, client_sock]).start()
        del client_sock, addr

def vm_loop(vm, secret, sock):
    if not validate_secret(sock, secret):
        return

    client = sock.makefile('rw', 1)
    while True:
        request = json.loads(client.readline())
        process_request(vm, request)

def validate_secret(sock, secret):
    sock.settimeout(2.0)

    client = sock.makefile('rw')
    got_secret = client.readline()
    if got_secret.strip() != secret:
        sock.close()
        logging.error('invalid auth')
        return False

    sock.settimeout(None)
    return True

def process_request(vm, request):
    print('VM', vm, 'request', request)
