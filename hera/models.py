import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hera.settings'

from django.db import models
from django.db import transaction
from django.contrib.auth import models as auth_models
from django.core.exceptions import PermissionDenied

import datetime
import os
import jsonfield
import binascii
import json

def MoneyField(*args, **kwargs):
    return models.DecimalField(*args, decimal_places=10, max_digits=20, **kwargs)

class VM(models.Model):
    creator = models.ForeignKey('Account')
    stats = jsonfield.JSONField(blank=True, null=True)
    vm_id = models.CharField(max_length=120)
    address = models.CharField(max_length=120)

    @property
    def stats_parsed(self):
        return json.loads(self.stats)

    def get_privileged_account(self, user):
        if not self.creator.is_privileged(user):
            raise PermissionDenied()
        return self.creator

    def is_user_privileged(self, user):
        self.get_privileged_account(user)

class QueuedCreation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    params = jsonfield.JSONField()

    resource = models.ForeignKey('DerivativeResource')
    vm = models.ForeignKey('VM', null=True, blank=True)
    stats = jsonfield.JSONField()
    owner = models.ForeignKey('Account')

class DerivativeResource(models.Model):
    owner = models.ForeignKey('Account')
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    closed_at = models.DateTimeField(null=True)

    base_price_per_second = MoneyField()
    custom = jsonfield.JSONField(blank=True, null=True)

    user_type = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)

    @property
    def expired(self):
        return datetime.datetime.now() > self.expiry

    @property
    def running_time(self):
        if self.closed_at:
            return self.closed_at - self.created
        else:
            return self.expiry - self.created

    def close(self):
        if self.id:
            if not self.closed_at:
                self.closed_at = datetime.datetime.now()
            self.save()

    def __str__(self):
        return 'DerivativeResource (%s, %s)' % (self.user_type, self.user_id)

class DerivativeResourceUsed(models.Model):
    resource = models.ForeignKey(DerivativeResource)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = MoneyField()

class Account(models.Model):
    billing_owner = models.ForeignKey(auth_models.User,
                                      related_name='accounts')
    is_main = models.BooleanField()
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=50)

    price_per_second_limit = models.FloatField(default=1e100)
    price_used = MoneyField(default=0.0)
    price_transferred_to = MoneyField(default=0.0)

    @property
    def price_balance(self):
        return self.price_transferred_to - self.price_used

    def __str__(self):
        return 'Account ' + self.name

    def get_api_key(self):
        if not self.api_key:
            self.regen_api_key()
            self.save()
        return self.api_key.encode()

    def regen_api_key(self):
        self.api_key = binascii.hexlify(os.urandom(16)).decode()

    def is_privileged(self, user):
        return user == self.billing_owner

    @property
    def api_auth(self):
        return (self.name, self.api_key)

    @classmethod
    def get_account(self, name):
        try:
            return Account.objects.get(name=name)
        except Account.DoesNotExist as err:
            # maybe main account not yet created for user?
            try:
                user = auth_models.User.objects.get(username=name)
            except auth_models.User.DoesNotExist:
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

    def is_privileged(self, account):
        return account == self.owner

class Template(models.Model):
    owner = models.ForeignKey('Account', null=True, blank=True, related_name='templates')
    public = models.BooleanField(default=False)
    disk = models.ForeignKey('Disk')
    name = models.CharField(max_length=300, null=True, blank=True)

    def is_privileged(self, account, operation):
        if operation == 'read' and self.public:
            return True
        else:
            return account == self.owner
