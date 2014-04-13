# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Disk'
        db.create_table('hera_disk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.Owner'], null=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('refcount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('hera', ['Disk'])


    def backwards(self, orm):
        # Deleting model 'Disk'
        db.delete_table('hera_disk')


    models = {
        'hera.derivativeresource': {
            'Meta': {'object_name': 'DerivativeResource'},
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Owner']"}),
            'timeout': ('django.db.models.fields.FloatField', [], {})
        },
        'hera.disk': {
            'Meta': {'object_name': 'Disk'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Owner']", 'null': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'refcount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'hera.owner': {
            'Meta': {'object_name': 'Owner'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hera.resourcerefreshed': {
            'Meta': {'object_name': 'ResourceRefreshed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.DerivativeResource']", 'related_name': "'refreshes'"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'})
        },
        'hera.vm': {
            'Meta': {'object_name': 'VM'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vm_id': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['hera']