import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import heraclient
s = heraclient.Sandbox.create(timeout=15, disk=heraclient.new_disk(size='10M'))
proc = s.execute(chroot=False, sync=True, args=['busybox', 'sh', '-c',
                                                'echo hello > /mnt/world'])
template = s.save_as_template()
print('Saved as template with id:', template.id)
