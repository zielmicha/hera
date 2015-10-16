import uuid
import os
import traceback
import socket
import logging
import threading
import json
import time
import struct
import binascii

from hera import vmcontroller
from hera import accounting
from hera import settings
from hera import disks

HALT_TIMEOUT = 0.2
TIME_BETWEEN_REGISTRATIONS = 2

def spawn(request):
    sock = socket.socket()
    sock.bind(('0.0.0.0', 0))
    sock.listen(1)

    port = sock.getsockname()[1]
    secret = str(uuid.uuid4())
    vm_id = str(uuid.uuid4())

    logging.info('Spawning VM with config %r on port %d', request, port)

    pid = os.fork()
    if pid == 0:
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
        return [vm_id, socket.getfqdn(), port, secret], pid

class Server:
    def __init__(self, owner, stats, res_id, vm_id, secret, server_sock):
        self.owner = owner
        self.stats = stats
        self.res_id = res_id
        self.vm_id = vm_id
        self.secret = secret
        self.server_sock = server_sock
        self.disk = None
        self.start_time = time.time()
        self.last_resource_registration = 0

    def loop(self):
        self.init()
        self.server_loop()

    def register_resource(self):
        accounting.derivative_resource_used(self.res_id, user_type='vm',
                                            user_id=self.vm_id)

    def init(self):
        def heartbeat_callback():
            time_left = time.time() - self.start_time
            if time.time() - self.last_resource_registration > TIME_BETWEEN_REGISTRATIONS:
                self.last_resource_registration = time.time()
                threading.Thread(target=self.register_resource).start()
            if time_left > self.stats['timeout']:
                self.vm.close()

        self.vm = vmcontroller.VM(
            heartbeat_callback=heartbeat_callback,
            close_callback=self.after_close)

        self.disk = disks.clone_or_create_disk(self.stats['disk'],
                                               owner=self.owner,
                                               timeout=self.stats['timeout'])
        self.vm.log('Disk ready')

        self.vm.start(
            memory=self.stats['memory'],
            disk=self.disk.path,
            id=self.res_id,
            cmdline=self.get_cmdline())

    def get_cmdline(self):
        proxy_local = settings.PROXY_RAW_ADDR
        cmdline = 'hera.proxy_local=%s:%d' % proxy_local
        cmdline += ' hera.proxy_ws_remote=' + settings.PROXY_WS
        cmdline += ' hera.proxy_http_remote=' + settings.PROXY_HTTP
        if self.disk.new:
            cmdline += ' hera.format_disk=true'
        cmdline += ' hera.seed=' + binascii.hexlify(os.urandom(32)).decode()
        cmdline += ' ' + self.get_ip_config()
        return cmdline

    def get_ip_config(self):
        def numip(i):
            return socket.inet_ntoa(struct.pack('!I', i))
        ip_count = 2**(32-9)
        ip_id = (self.get_ip_id() % (ip_count - 1)) + 1
        net = '10.128.0.0'
        neti, = struct.unpack('!I', socket.inet_aton(net))
        return 'ip=%s::%s:255.128.0.0:sandbox' % (numip(neti + ip_id), numip(neti + 1))

    def get_ip_id(self):
        return uuid.UUID(self.vm_id).int

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
        if not isinstance(request, dict) or 'type' not in request:
            logging.error('malformed request: %r', request)
            return {'status': 'MalformedRequest'}
        type = request['type']
        if type == 'kill':
            self.vm.close()
            return {'status': 'ok'}
        elif type == 'create_template':
            return self.create_template(request.get('name'))
        else:
            return self.vm.send_message(request)

    def create_template(self, name):
        disk = self.disk
        self.disk = None # keep disk from beging GCed

        resp = self.vm.send_message({'type': 'prepare_for_death'})
        if resp['status'] != 'ok':
            return resp

        self.vm.send_message({'type': 'halt'}, want_reply=False)
        time.sleep(HALT_TIMEOUT)
        template = disk.save_as_template(name)

        disk.decref()
        return {'status': 'ok', 'id': template.id}

    def after_close(self):
        self.server_sock.close()
        if self.disk:
            self.disk.decref()
            self.disk = None
        accounting.derivative_resource_closed(self.res_id)

        os._exit(0)
