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

LAUNCH_TIMEOUT = 40
HEARTBEAT_TIMEOUT = 40
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

        self.netd_connection = None

        self.lock = threading.Lock()
        self.closed = False

    def start(self, **kwargs):
        self.start_server()
        self.start_qemu(**kwargs)

    def start_qemu(self, memory, disk, id=1, cmdline=''):
        tap_name = self.get_tap()
        args = [
            'qemu-system-x86_64',
            '-bios', 'deps/qboot/bios.bin',
            '-enable-kvm',
            '-kernel', 'agent/build/kernel',
            '-initrd', 'agent/build/ramdisk',
            '-append', cmdline + ' console=ttyS0 quiet',
            '-serial', 'mon:stdio',
            '-nographic',
## Disk
            '-drive', 'file=%s,if=virtio,cache=none' % disk,
## Virtio serial:
            '-device', 'virtio-serial',
            '-chardev', 'socket,id=agent,path=' + self.socket_name,
            '-device', 'virtserialport,chardev=agent,name=hera.agent',
## Network
            '-net', 'tap,ifname=%s,script=no,downscript=no' % tap_name,
            '-net', 'nic,model=virtio',
## Memory
            '-m', str(memory),
        ]
        devnull = open('/dev/null', 'r+')
        self.process = subprocess.Popen(args,
                                        #stdout=devnull,
                                        stdin=devnull)

    def get_tap(self):
        self.netd_connection = socket.socket(socket.AF_UNIX)
        self.netd_connection.connect('/var/run/hera.netd.%d.sock' % os.getuid())
        name = self.netd_connection.makefile('r', 1).readline().strip()
        if not name:
            raise Exception('netd call failed')
        self.log('acquired TAP device')
        return name

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
        self.log(resp)
        if 'outofband' in resp:
            oob_type = resp['outofband']
            if oob_type == 'heartbeat':
                if not self.closed:
                    self.heartbeat_callback()
        else:
            self.read_queue.put(resp)

    def log(self, txt):
        print('[%f]' % (time.time() - self.init_time), txt)

    def _writer(self, file):
        while True:
            q = self.write_queue.get()
            if q == CLOSE: break
            message, callback = q
            file.write(message)
            file.flush()
            response = self.read_queue.get()
            callback(response)

    def send_message(self, message, want_reply=True):
        event = threading.Event()
        result = [None]

        def callback(resp):
            result[0] = resp
            event.set()

        message_data = json.dumps(message) + '\n'
        self.write_queue.put((message_data, callback))

        if not want_reply:
            return

        if event.wait(timeout=MESSAGE_REPLY_TIMEOUT):
            return result[0]
        else:
            raise errors.TimeoutError()

    def close(self):
        with self.lock:
            # ensure close occurs only once
            if self.closed:
                return
            self.closed = True

        self.write_queue.put(CLOSE)
        self._kill_qemu()

        if self.netd_connection:
            self.netd_connection.close()

        self.close_callback()

    def _kill_qemu(self):
        if self.process:
            self.process.kill()
            self.process = None

if __name__ == '__main__':
    vm = VM()
    vm.start(memory=128)
    try:
        print(vm.send_message({'hello': 'world'}))
        input('Press enter to terminate.\n')
    finally:
        print('terminate')
        vm.close()
