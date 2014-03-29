import socket
import subprocess
import os
import tempfile
import threading
import time

class VM:
    def __init__(self):
        self.pid = None
        self.init_time = time.time()
        self.process = None

    def start(self):
        self.start_server()
        self.start_qemu()

    def start_qemu(self):
        args = [
            'qemu-system-x86_64',
            '-enable-kvm',
            '-kernel', 'agent/build/kernel',
            '-initrd', 'agent/build/ramdisk',
            '-append', 'quiet', #ip=dhcp
#            '-nographic',
## Virtio serial:
            '-device', 'virtio-serial',
            '-chardev', 'socket,id=agent,path=' + self.socket_name,
            '-device', 'virtserialport,chardev=agent,name=hera.agent',
            '-net', 'user',
            '-net', 'nic,model=rtl8139',
        ]
        devnull = open('/dev/null', 'r+')
        self.process = subprocess.Popen(args,
                                        stdin=devnull)

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
        print 'run_server'
        while True:
            line = file.readline()
            if not line:
                break
            print '[%f]' % (time.time() - self.init_time), line.rstrip()
        print 'vport disconnect'
        self.close()

    def _server_accept_connection(self, server):
        server.settimeout(5)
        server.listen(1)
        try:
            try:
                sock, addr = server.accept()
            except socket.error:
                # timeout
                self._kill_qemu()
                raise Exception("qemu didn't respond in time")
        finally:
            os.unlink(self.socket_name)
            os.rmdir(self.socket_dir)
        return sock, sock.makefile('r+')

    def close(self):
        self._kill_qemu()

    def _kill_qemu(self):
        if self.process:
            self.process.kill()

if __name__ == '__main__':
    vm = VM()
    vm.start()
    try:
        raw_input('Press enter to terminate.\n')
    finally:
        print 'terminate'
        vm.close()
