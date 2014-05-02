from django.db.models import F
from django.db import transaction
from django.core.exceptions import PermissionDenied
from hera import models
from hera import settings

import os
import subprocess

sizes = {
    'k': 1000,
    'M': 1000*1000,
    'G': 1000*1000*1000,
}

def clone_or_create_disk(id, owner, timeout):
    owner_account = models.Account.get_account(owner)
    if isinstance(id, str) and id.startswith('new,'):
        return create_disk(id[4:], owner_account, timeout)
    else:
        template = models.Template.objects.get(id=int(id))
        if not template.is_privileged(owner_account, 'read'):
            raise PermissionDenied()
        return Disk.clone(template, owner=owner_account, timeout=timeout)

def create_disk(request, owner, timeout):
    size = parse_size(request)
    disk_model = models.Disk(owner=owner, refcount=1, timeout=timeout)
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
        self.decref_done = False

    def create(self, size):
        subprocess.check_call(['qemu-img', 'create',
                               '-f', 'qcow2', self.path, '%d' % size])
        self.new = True

    def create_with_backing(self, path):
        subprocess.check_call(['qemu-img', 'create',
                               '-f', 'qcow2',
                               '-b', path,
                               self.path])

    @transaction.atomic
    def change_ref(self, dir):
        models.Disk.objects.filter(pk=self.model.pk).update(
            refcount=F('refcount') + dir)
        self.model = models.Disk.objects.get(pk=self.model.pk)
        if self.model.refcount == 0:
            if self.model.backing:
                backing = Disk(self.model.backing)
                backing.decref()
            try:
                os.remove(self.path)
            except FileNotFoundError:
                pass

    def decref(self):
        # Just a guard: encsure that we don't decref same use twice
        assert not self.decref_done
        self.decref_done = True
        self.change_ref(-1)

    def incref(self):
        self.change_ref(+1)

    @transaction.atomic
    def save_as_template(self, name):
        template = models.Template(owner=self.model.owner,
                                   public=False,
                                   disk=self.model,
                                   name=name)
        template.save()
        self.incref()
        return template

    @classmethod
    @transaction.atomic
    def clone(cls, template, owner, timeout):
        new_disk = models.Disk(owner=owner,
                               refcount=1,
                               timeout=timeout)
        new_disk.backing = template.disk
        new_disk.save()

        orig = Disk(template.disk)
        orig.timeout = float('inf')
        orig.incref()

        new = Disk(new_disk)
        new.create_with_backing(orig.path)
        return new
