# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hera', '0002_auto_20151018_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuedcreation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 26, 8, 28, 50, 87800), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='queuedcreation',
            name='params',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=False,
        ),
    ]
