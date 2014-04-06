import socket
import subprocess
import os
import tempfile
import threading
import time
import json
import queue

from hera import errors
from hera import util

LAUNCH_TIMEOUT = 6
HEARTBEAT_TIMEOUT = 2
MESSAGE_REPLY_TIMEOUT = LAUNCH_TIMEOUT

CLOSE = object()

class VM:
    def __init__(self,
                 heartbeat_callback=util.do_nothing,
                 close_callback=util.do_nothing):
        self.init_time = time.time()
        self.process = None
        self.write_queue = queue.Queue(0)
        self.read_queue = queue.Queue(0)
        self.heartbeat_callback = heartbeat_callback
        self.close_callback = close_callback

    def start(self, **kwargs):
        self.start_server()
        self.start_qemu(**kwargs)

    def start_qemu(self, memory):
        args = [
            'qemu-system-x86_64',
            '-enable-kvm',
            '-kernel', 'agent/build/kernel',
            '-initrd', 'agent/build/ramdisk',
            '-append', 'quiet ip=dhcp',
            '-nographic',
## Virtio serial:
            '-device', 'virtio-serial',
            '-chardev', 'socket,id=agent,path=' + self.socket_name,
            '-device', 'virtserialport,chardev=agent,name=hera.agent',
## Network
            '-net', 'user',
            '-net', 'nic,model=rtl8139',
## Memory
            '-m', str(memory),
        ]
        devnull = open('/dev/null', 'r+')
        self.process = subprocess.Popen(args,
                                        stdin=devnull,
                                        stdout=devnull)

    def start_server(self):
        sock = socket.socket(socket.AF_UNIX)
        self.socket_dir = tempfile.mkdtemp(prefix='hera.vmcontroller.')
        self.socket_name = self.socket_dir + '/socket'
        os.chmod(self.socket_dir, 0o700)
        sock.bind(self.socket_name)
        os.chmod(self.socket_name, 0o700)
        threading.Thread(target=self.run_server, args=[sock]).start()

    def run_server(self, server):
        socket, file = self._server_accept_connection(server)
        threading.Thread(target=self._writer, args=[file]).start()

        try:
            while True:
                line = file.readline()
                if not line:
                    break
                resp = json.loads(line)
                self._process_response(resp)
                socket.settimeout(HEARTBEAT_TIMEOUT)
        finally:
            self.close()

    def _server_accept_connection(self, server):
        server.settimeout(LAUNCH_TIMEOUT)
        server.listen(1)
        try:
            try:
                sock, addr = server.accept()
            except socket.error:
                # timeout
                self.close()
                raise Exception("qemu didn't respond in time")
        finally:
            os.unlink(self.socket_name)
            os.rmdir(self.socket_dir)

        sock.settimeout(LAUNCH_TIMEOUT)
        return sock, sock.makefile('rw')

    def _process_response(self, resp):
        print('[%f]' % (time.time() - self.init_time), resp)
        if 'outofband' in resp:
            oob_type = resp['outofband']
            if oob_type == 'heartbeat':
                self.heartbeat_callback()
        else:
            self.read_queue.put(resp)

    def _writer(self, file):
        while True:
            q = self.write_queue.get()
            if q == CLOSE: break
            message, callback = q
            file.write(message)
            file.flush()
            response = self.read_queue.get()
            callback(response)

    def send_message(self, message):
        event = threading.Event()
        result = [None]

        def callback(resp):
            result[0] = resp
            event.set()

        message_data = json.dumps(message) + '\n'
        self.write_queue.put((message_data, callback))
        if event.wait(timeout=MESSAGE_REPLY_TIMEOUT):
            return result[0]
        else:
            raise errors.TimeoutError()

    def close(self):
        self.write_queue.put(CLOSE)
        self._kill_qemu()
        self.close_callback()

    def _kill_qemu(self):
        if self.process:
            self.process.kill()

if __name__ == '__main__':
    vm = VM()
    vm.start(memory=128)
    try:
        print(vm.send_message({'hello': 'world'}))
        input('Press enter to terminate.\n')
    finally:
        print('terminate')
        vm.close()
