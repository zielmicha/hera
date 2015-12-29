#!/usr/bin/env python
from __future__ import print_function
import argparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

parser = argparse.ArgumentParser()
parser.add_argument('source', help='Source name.')
parser.add_argument('target', help='Target name.')
parser.add_argument('command', nargs=argparse.REMAINDER)
ns = parser.parse_args()

import heraclient

def pipe(proc):
    while True:
        data = proc.stdout.read_some()
        if not data: break
        sys.stdout.write(data)
        sys.stdout.flush()

print('Creating VM')
s = heraclient.Sandbox.create(timeout=1800, disk=ns.source)
print('Waiting for VM')
s.wait()
for command in ns.command:
    print('Executing command:', command)
    proc = s.execute(stderr_to_stdout=True, args=['sh', '-c', command])
    pipe(proc)
    print('OK')

template = s.save_as_template(name=ns.target)
print('Saved as template with id:', template.id)
