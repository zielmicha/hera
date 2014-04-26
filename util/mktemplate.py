#!/usr/bin/env python2
import argparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

parser = argparse.ArgumentParser()
parser.add_argument('image', help='Source tgz (created by ./mkdebian.sh).')
ns = parser.parse_args()

import heraclient
disk = heraclient.new_disk(size='10G')

print('Creating VM')
s = heraclient.Sandbox.create(timeout=300, disk=disk)
print('Waiting for VM')
s.wait()
print('Unpacking')
s.unpack(
    target='/',
    archive_type='tar',
    archive=ns.image)
print('OK')

#template = s.save_as_template()
#print('Saved as template with id:', template.id)
