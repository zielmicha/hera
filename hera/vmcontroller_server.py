import uuid
import os
import traceback
import socket
import logging
import threading
import json
import time

from hera import vmcontroller
from hera import accounting

def spawn(request):
    sock = socket.socket()
    sock.bind(('0.0.0.0', 0))
    sock.listen(1)

    port = sock.getsockname()[1]
    secret = str(uuid.uuid4())
    vm_id = str(uuid.uuid4())

    logging.info('Spawning VM with config %r on port %d', request, port)
    if os.fork() == 0:
        try:
            Server(owner=request['owner'],
                   stats=request['stats'],
                   res_id=request['res_id'],
                   vm_id=vm_id,
                   secret=secret,
                   server_sock=sock).loop()
        except:
            traceback.print_exc()
        finally:
            os._exit(1)
    else:
        sock.close()
        return [vm_id, socket.getfqdn(), port, secret]

class Server:
    def __init__(self, owner, stats, res_id, vm_id, secret, server_sock):
        self.stats = stats
        self.res_id = res_id
        self.vm_id = vm_id
        self.secret = secret
        self.server_sock = server_sock
        self.start_time = time.time()

    def loop(self):
        self.init()
        self.server_loop()

    def init(self):
        def heartbeat_callback():
            time_left = time.time() - self.start_time
            if time_left > self.stats['timeout']:
                self.vm.close()
            accounting.derivative_resource_used(self.res_id, user_type='vm',
                                                user_id=self.vm_id)

        self.vm = vmcontroller.VM(
            heartbeat_callback=heartbeat_callback,
            close_callback=self.after_close)

        self.vm.start(
            memory=self.stats['memory'])

    def server_loop(self):
        while True:
            try:
                client_sock, addr = self.server_sock.accept()
            except OSError: # server_sock.close() called
                return
            threading.Thread(target=self.client_loop,
                             args=[client_sock]).start()
            del client_sock, addr

    def client_loop(self, sock):
        client = sock.makefile('rw', 1)

        if not self.validate_secret(sock, client):
            return

        while True:
            line = client.readline()
            if not line:
                break
            request = json.loads(line)
            response = self.process_request(request)
            client.write(json.dumps(response) + '\n')

    def validate_secret(self, sock, file):
        sock.settimeout(2.0)

        got_secret = file.readline()
        if got_secret.strip() != self.secret:
            sock.close()
            logging.error('invalid auth')
            return False

        sock.settimeout(None)
        return True

    def process_request(self, request):
        type = request['type']
        if type == 'kill':
            self.vm.close()
            return {'status': 'ok'}
        else:
            return self.vm.send_message(request)

    def after_close(self):
        self.server_sock.close()
