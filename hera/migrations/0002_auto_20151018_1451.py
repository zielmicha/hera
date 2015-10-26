# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hera', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueuedCreation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('stats', jsonfield.fields.JSONField()),
                ('owner', models.ForeignKey(to='hera.Account')),
                ('resource', models.ForeignKey(to='hera.DerivativeResource')),
                ('vm', models.ForeignKey(null=True, blank=True, to='hera.VM')),
            ],
        ),
        migrations.AlterField(
            model_name='derivativeresourceused',
            name='end_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='derivativeresourceused',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]
