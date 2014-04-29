import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hera.settings'

from django.db import models
from django.db import transaction
from django.contrib.auth import models as auth_models
import datetime
import os
import jsonfield
import binascii

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

    def __str__(self):
        return 'DerivativeResource (%s, %s)' % (self.user_type, self.user_id)

class DerivativeResourceUsed(models.Model):
    resource = models.ForeignKey(DerivativeResource)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True)
    prize = models.FloatField()

class Account(models.Model):
    billing_owner = models.ForeignKey(auth_models.User,
                                      related_name='accounts')
    is_main = models.BooleanField()
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=50)

    prize_per_second_limit = models.FloatField(default=1e100)
    prize_used = models.FloatField(default=0.0)
    prize_transferred_to = models.FloatField(default=0.0)

    def __str__(self):
        return 'Account ' + self.name

    def get_api_key(self):
        if not self.api_key:
            self.regen_api_key()
            self.save()
        return self.api_key

    def regen_api_key(self):
        self.api_key = binascii.hexlify(os.urandom(16))

    def is_privileged(self, user):
        return user == self.billing_owner

    @classmethod
    def get_account(self, name):
        try:
            return Account.objects.get(name=name)
        except Account.DoesNotExist as err:
            # maybe main account not yet created for user?
            try:
                user = auth_models.User.objects.get(username=name)
            except Account.DoesNotExist:
                raise err
            else:
                return Account.get_main_for_user(user)

    @classmethod
    @transaction.atomic
    def get_main_for_user(self, user):
        account, _ = self.objects.get_or_create(billing_owner=user, is_main=True,
                                                defaults=dict(name=user.username))
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
