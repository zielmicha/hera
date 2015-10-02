#!/usr/bin/env python3
import subprocess
import os
import select
import atexit
import sys
import pty
import traceback
import time

os.environ['PYTHONUNBUFFERED'] = '1'

tasks = [
    'apiserver', 'dispatcher', 'django', 'netd', 'nginx', 'proxy', 'spawner'
]

CG = '/sys/fs/cgroup/cpu/hera'
if not os.access(CG + '/tasks', os.O_RDWR):
    sys.exit('Create cgroup %r and make it writable to user %d (or run `make cgroup`)'
             % (CG, os.getuid()))

def preexec():
    with open(CG + '/tasks', 'a') as f:
        f.write(str(os.getpid()) + '\n')

preexec()

class PtyPopen():
    def __init__(self, args):
        self.args = args
        pid, master = pty.fork()
        if pid == 0:
            try:
                self._child()
            except:
                traceback.print_exc()
            finally:
                os._exit(0)
        else:
            self.stdout = os.fdopen(master, 'rb', 1)

    def _child(self):
        os.execvp(self.args[0], self.args)

procs = {}
for task in tasks:
    procs[task] = PtyPopen(['make', 'run_' + task])

def finish():
    for i in range(5):
        tasks = open(CG + '/tasks').read().split()
        tasks = [ pid for pid in tasks
                  if int(pid) != os.getpid() ]

        print('[Killing tasks: %s]' % ' '.join(tasks))

        if i == 0:
            sig = 15
        else:
            sig = 9
        if not tasks: break
        subprocess.call(['sudo', 'kill', '-%d' % sig] + tasks)
        time.sleep(0.3)

atexit.register(finish)

reset_colors = '\033[0m'

while True:
    r, w, x = select.select([ p.stdout for p in procs.values() ], [], [])
    for stream in r:
        name = [ k for k, v in procs.items() if v.stdout == stream ][0]

        data = '[%s] ' % (name.ljust(10), )
        sys.stdout.buffer.write(data.encode())
        sys.stdout.buffer.flush()

        ret = stream.readline()

        if not ret:
            del procs[name]
            ret = r'{exited}'

        sys.stdout.buffer.write(ret)
        sys.stdout.buffer.write(reset_colors.encode())
        sys.stdout.buffer.flush()
