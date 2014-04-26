import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import heraclient

disk = heraclient.new_disk(size='10M')

s = heraclient.Sandbox.create(timeout=15, disk=disk)
s.unpack(
    target='/',
    archive_type='zip',
    archive=os.path.dirname(__file__) + '/foo.zip')
s.unpack(
    target='/',
    archive_type='tar',
    archive=os.path.dirname(__file__) + '/bar.tgz')

print(s.execute(['busybox', 'ls', '/mnt'], chroot=False).read_stdout())
