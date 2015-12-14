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
            name='TerminalRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('streams', jsonfield.fields.JSONField()),
                ('vm', models.ForeignKey(to='hera.VM')),
            ],
        ),
    ]
