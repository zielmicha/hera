import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import heraclient

disk = heraclient.new_disk(size='10M')

s = heraclient.Sandbox.create(timeout=15, disk=disk)
proc = s.execute(chroot=False, sync=False, args=['busybox', 'cat'])
proc.stdin.upload(b'hello\n')
stream = proc.stdout.download()
print(repr(stream.read(5)))
print('And rest:')
print(repr(stream.read()))
