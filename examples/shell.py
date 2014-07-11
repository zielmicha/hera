import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import heraclient
import argparse
import threading
import atexit
import termios
import tty

parser = argparse.ArgumentParser(description='Run shell.')
parser.add_argument('template',
                   help='use template')
parser.add_argument('--no-chroot', dest='chroot', action='store_false',
                    default=True,
                    help='run initial busybox')
args = parser.parse_args()

s = heraclient.Sandbox.create(timeout=40, disk=args.template,
                              memory=64)

def terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return h, w

if args.chroot:
    proc = s.execute(args=['bash', '-i'],
                     stderr_to_stdout=True,
                     pty_size=terminal_size())
else:
    proc = s.execute(args=['busybox', 'sh', '-i'],
                     chroot=False,
                     stderr_to_stdout=True,
                     pty_size=None)

def rev():
    while True:
        ch = sys.stdin.read(1)
        if not ch:
            proc.stdin.close()
            return
        proc.stdin.write(ch)

t = threading.Thread(target=rev)
t.daemon = True
t.start()

if args.chroot:
    old = termios.tcgetattr(0)
    atexit.register(termios.tcsetattr, 0, termios.TCSADRAIN, old)
    tty.setcbreak(0)

atexit.register(s.kill)

while True:
    data = proc.stdout.read_some()
    if not data: break
    sys.stdout.write(data)
    sys.stdout.flush()
