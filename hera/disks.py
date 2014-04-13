from django.db.models import F
from hera import models
from hera import settings

import os
import subprocess

sizes = {
    'k': 1000,
    'M': 1000*1000,
    'G': 1000*1000*1000,
}

def get_or_create_disk(id, owner):
    if id.startswith('new,'):
        return create_disk(id[4:], owner)
    else:
        disk = models.Disk.objects.get(id=int(id))
        disk.check_owner(owner)
        return Disk(disk)

def create_disk(request, owner):
    size = parse_size(request)
    disk_model = models.Disk(owner=None, refcount=1)
    disk_model.save()
    disk = Disk(disk_model)
    disk.create(size)
    return disk

def parse_size(s):
    multiplier = 1
    if s[-1] in sizes:
        multiplier = sizes[s[-1]]
        s = s[:-1]
    return int(s) * multiplier

class Disk:
    def __init__(self, model):
        self.model = model
        self.path = settings.IMAGE_STORAGE + ('/%d.img' % model.id)
        self.new = False

    def create(self, size):
        subprocess.check_call(['qemu-img', 'create',
                               '-f', 'qcow2', self.path, '%d' % size])
        self.new = True

    def change_ref(self, dir):
        self.model.refcount = F('refcount') + dir
        self.model.save()
        self.model = models.Disk.objects.get(pk=self.model.pk)
        if self.model.refcount == 0:
            try:
                os.remove(self.path)
            except FileNotFoundError:
                pass

    def decref(self):
        self.change_ref(-1)
