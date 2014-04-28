import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hera.settings'

from django.db import models
from django.db import transaction
from django.contrib.auth import models as auth_models
import datetime
import os
import jsonfield

class VM(models.Model):
    creator = models.ForeignKey('Account')
    stats = jsonfield.JSONField()
    vm_id = models.CharField(max_length=120)
    address = models.CharField(max_length=120)

class DerivativeResource(models.Model):
    owner = models.ForeignKey('Account')
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    closed_at = models.DateTimeField(null=True)

    base_prize_per_second = models.FloatField()
    custom = jsonfield.JSONField()

    user_type = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)

    def close(self):
        if self.id:
            if not self.closed_at:
                self.closed_at = datetime.datetime.now()
            self.save()

class DerivativeResourceUsed(models.Model):
    resource = models.ForeignKey(DerivativeResource)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True)
    prize = models.FloatField()

class Account(models.Model):
    billing_owner = models.ForeignKey(auth_models.User)
    is_main = models.BooleanField()
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=50)

    prize_per_second_limit = models.FloatField()
    prize_used = models.FloatField()
    prize_transferred_to = models.FloatField()

    def get_api_key(self):
        if not self.api_key:
            self.regen_api_key()
            self.save()
        return self.api_key

    def regen_api_key(self):
        self.api_key = os.urandom(16).encode('hex')

    @transaction.atomic
    @classmethod
    def get_main_for_user(self, user):
        account, _ = self.objects.get_or_create(billing_owner=user, is_main=True,
                                                defaults=dict(name=user.name))
        return account

class Disk(models.Model):
    owner = models.ForeignKey('Account', null=True, blank=True)
    refcount = models.IntegerField(default=0)
    backing = models.ForeignKey('Disk', null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    timeout = models.FloatField(default=1e100)

    def check_owner(self, owner):
        pass

class Template(models.Model):
    owner = models.ForeignKey('Account', null=True, blank=True)
    public = models.BooleanField(default=False)
    disk = models.ForeignKey('Disk')
    name = models.CharField(max_length=300, null=True, blank=True)

    def check_owner(self, owner):
        pass
