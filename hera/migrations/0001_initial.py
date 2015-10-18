# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_main', models.BooleanField()),
                ('name', models.CharField(unique=True, max_length=100)),
                ('api_key', models.CharField(max_length=50)),
                ('price_per_second_limit', models.FloatField(default=1e+100)),
                ('price_used', models.DecimalField(default=0.0, max_digits=20, decimal_places=10)),
                ('price_transferred_to', models.DecimalField(default=0.0, max_digits=20, decimal_places=10)),
                ('billing_owner', models.ForeignKey(related_name='accounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DerivativeResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expiry', models.DateTimeField()),
                ('closed_at', models.DateTimeField(null=True)),
                ('base_price_per_second', models.DecimalField(max_digits=20, decimal_places=10)),
                ('custom', jsonfield.fields.JSONField(null=True, blank=True)),
                ('user_type', models.CharField(max_length=100)),
                ('user_id', models.CharField(max_length=100)),
                ('owner', models.ForeignKey(to='hera.Account')),
            ],
        ),
        migrations.CreateModel(
            name='DerivativeResourceUsed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=20, decimal_places=10)),
                ('resource', models.ForeignKey(to='hera.DerivativeResource')),
            ],
        ),
        migrations.CreateModel(
            name='Disk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refcount', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('timeout', models.FloatField(default=1e+100)),
                ('backing', models.ForeignKey(to='hera.Disk', null=True, blank=True)),
                ('owner', models.ForeignKey(to='hera.Account', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public', models.BooleanField(default=False)),
                ('name', models.CharField(null=True, max_length=300, blank=True)),
                ('disk', models.ForeignKey(to='hera.Disk')),
                ('owner', models.ForeignKey(to='hera.Account', related_name='templates', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='VM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stats', jsonfield.fields.JSONField(null=True, blank=True)),
                ('vm_id', models.CharField(max_length=120)),
                ('address', models.CharField(max_length=120)),
                ('creator', models.ForeignKey(to='hera.Account')),
            ],
        ),
    ]
