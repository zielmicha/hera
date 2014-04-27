import subprocess
import socket
import argparse
import os
import threading
import pwd

parser = argparse.ArgumentParser(description='''
Call like this:
sudo python hera/netd.py $(id -u)
''')
parser.add_argument('uid', help='Unpriviliged user id.', type=int)
ns = parser.parse_args()
user_name = pwd.getpwuid(ns.uid).pw_name

subprocess.call('brctl addbr brhera', shell=True)
subprocess.check_call('ifconfig brhera 10.128.0.1/9', shell=True)

socket_path = '/var/run/hera.netd.%d.sock' % ns.uid
sock = socket.socket(socket.AF_UNIX)
if os.path.exists(socket_path):
    os.remove(socket_path)
sock.bind(socket_path)
os.chmod(socket_path, 0o700)
os.chown(socket_path, ns.uid, 0)
sock.listen(5)

def handle(conn):
    file = conn.makefile('rw', 1)
    tap_name = 'tap.hera.' + os.urandom(4).encode('hex')
    subprocess.check_call(['openvpn', '--mktun', '--dev', tap_name,
                           '--user', user_name])
    subprocess.check_call('ifconfig %s up 0.0.0.0 promisc' % tap_name, shell=True)
    subprocess.check_call('brctl addif brhera %s' % tap_name, shell=True)
    def exit():
        subprocess.call('openvpn --rmtun --dev %s' % tap_name, shell=True)

    try:
        file.write('%s\n' % tap_name)
        # wait for exit
        file.readline()
    finally:
        exit()

while True:
    conn, addr = sock.accept()
    threading.Thread(target=handle, args=[conn]).start()
    del conn
