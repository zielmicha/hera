import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import heraclient

disk = heraclient.new_disk(size='10M')

s = heraclient.Sandbox.create(timeout=15, disk=disk)
proc = s.execute(chroot=False, sync=False, args=['busybox', 'cat'])
for i in range(1000):
    print(i)
    msg = 'helloworld\n'
    proc.stdin.write(msg)
    if i % 2 == 0:
        l = proc.stdout.readline()
        assert l == msg, repr(l)
    else:
        assert proc.stdout.read(len(msg)) == msg
