from __future__ import print_function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import argparse
import heraclient

parser = argparse.ArgumentParser(description='Simple test.')
parser.add_argument('--template',
                   help='use template')
args = parser.parse_args()

if args.template:
    disk = args.template
else:
    disk = heraclient.new_disk(size='10M')

start = time.time()

def printdate(*args):
    print('[%.3f]' % (time.time() - start), *args)

s = heraclient.Sandbox.create(timeout=15, disk=disk)
printdate('`create` call returned')
proc = s.execute(chroot=False, sync=False, args=['busybox', 'cat', '/proc/cmdline'])
printdate('cmdline: %r' % (proc.read_stdout()))
proc = s.execute(chroot=False, sync=False, args=['busybox', 'ls', '/mnt'])
printdate('ls /mnt: %r' % (proc.read_stdout()))
proc = s.execute(chroot=False, sync=False, args=['busybox', 'ping', '10.128.0.1'])
printdate('ping: %r' % (proc.read_stdout()))

printdate('Took %.1f s' % (time.time() - start))
