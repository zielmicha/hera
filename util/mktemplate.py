#!/usr/bin/env python
import argparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

parser = argparse.ArgumentParser()
parser.add_argument('image', help='Source tgz (created by ./mkdebian.sh).')
parser.add_argument('target', help='Target name.')
ns = parser.parse_args()

import heraclient
disk = heraclient.new_disk(size='10G')

print('Creating VM')
s = heraclient.Sandbox.create(timeout=600, disk=disk)
print('Waiting for VM')
s.wait()
print('Unpacking')
s.unpack(
    target='/',
    archive_type='tar',
    compress_type='z',
    archive=ns.image)
print('OK')

print(s.execute(['busybox', 'ls', '/mnt'], chroot=False).read_stdout())
print(s.execute(['ls', '/']).read_stdout())
template = s.save_as_template(name=ns.target)
print('Saved as template with id:', template.id)
