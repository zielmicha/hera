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

s = heraclient.Sandbox.create(timeout=15, disk=disk)
proc = s.execute(chroot=False, sync=False, args=['busybox', 'cat', '/proc/cmdline'])
print('cmdline: %r' % (proc.read_stdout()))
proc = s.execute(chroot=False, sync=True, args=['busybox', 'ls', '/mnt'])
print('ls /mnt: %r' % (proc.read_stdout()))

print('Took %.1f s' % (time.time() - start))
