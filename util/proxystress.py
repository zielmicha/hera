import socket
import os

conns = []

for i in xrange(1000):
    s = socket.socket()
    s.connect(('localhost', 10003))
    s.sendall('id=%s\n' % os.urandom(5).encode('hex'))
    s.sendall('foo')
    conns.append(s)
