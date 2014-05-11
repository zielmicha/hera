#!/usr/bin/env python3
import subprocess
import os
import select
import atexit
import sys

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

procs = {}
for task in tasks:
    procs[task] = subprocess.Popen(['make', 'run_' + task],
                                   stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                                   close_fds=True, preexec_fn=preexec)

def finish():
    for pid in open(CG + '/tasks').read().split():
        pid = int(pid)
        if pid == os.getpid():
            continue
        try:
            os.kill(pid, 9)
        except OSError as err:
            print('[Failed to kill %d: %s]' % (pid, err))

atexit.register(finish)

while True:
    r, w, x = select.select([ p.stdout for p in procs.values() ], [], [])
    stream = r[0]
    name = [ k for k, v in procs.items() if v.stdout == stream ][0]
    ret = stream.readline()
    if not ret:
        del procs[name]
        ret = r'{exited}'
    else:
        data = '[%s] ' % (name.ljust(10), )
        sys.stdout.buffer.write(data.encode())
        sys.stdout.buffer.flush()
        sys.stdout.buffer.write(ret)
        sys.stdout.buffer.flush()
