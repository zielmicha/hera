import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hera.settings'

from django.db import models
import datetime

class VM(models.Model):
    vm_id = models.CharField(max_length=120)
    address = models.CharField(max_length=120)

class DerivativeResource(models.Model):
    owner = models.ForeignKey('Owner')
    created = models.DateTimeField(auto_now_add=True)
    timeout = models.FloatField()
    closed_at = models.DateTimeField(null=True)

    def close(self):
        if not self.closed_at:
            self.closed_at = datetime.datetime.now()
        self.put()

class ResourceRefreshed(models.Model):
    resource = models.ForeignKey(DerivativeResource, related_name='refreshes')
    time = models.DateTimeField(auto_now_add=True)

class Owner(models.Model):
    pass

class Disk(models.Model):
    owner = models.ForeignKey('Owner', null=True, blank=True)
    refcount = models.IntegerField(default=0)
    backing = models.ForeignKey('Disk', null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    timeout = models.FloatField(default=float('inf'))

    def check_owner(self, owner):
        pass

class Template(models.Model):
    owner = models.ForeignKey('Owner', null=True, blank=True)
    public = models.BooleanField(default=False)
    disk = models.ForeignKey('Disk')
    name = models.CharField(max_length=300, null=True, blank=True)

    def check_owner(self, owner):
        pass
