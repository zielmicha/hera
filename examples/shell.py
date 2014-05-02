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
args = parser.parse_args()

s = heraclient.Sandbox.create(timeout=40, disk=args.template,
                              memory=64)
proc = s.execute(args=['bash', '-i'], stderr_to_stdout=True)

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

old = termios.tcgetattr(0)
atexit.register(termios.tcsetattr, 0, termios.TCSADRAIN, old)
tty.setcbreak(0)
atexit.register(s.kill)

while True:
    data = proc.stdout.read_some()
    if not data: break
    sys.stdout.write(data)
    sys.stdout.flush()
