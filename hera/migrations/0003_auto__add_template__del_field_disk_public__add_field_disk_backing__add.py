# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Template'
        db.create_table('hera_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hera.Owner'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.Disk'])),
            ('name', self.gf('django.db.models.fields.CharField')(null=True, max_length=300)),
        ))
        db.send_create_signal('hera', ['Template'])

        # Deleting field 'Disk.public'
        db.delete_column('hera_disk', 'public')

        # Adding field 'Disk.backing'
        db.add_column('hera_disk', 'backing',
                      self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hera.Disk']),
                      keep_default=False)

        # Adding field 'Disk.created'
        db.add_column('hera_disk', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(blank=True, default=datetime.datetime(2014, 4, 14, 0, 0), auto_now_add=True),
                      keep_default=False)

        # Adding field 'Disk.timeout'
        db.add_column('hera_disk', 'timeout',
                      self.gf('django.db.models.fields.FloatField')(default=float('inf')),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Template'
        db.delete_table('hera_template')

        # Adding field 'Disk.public'
        db.add_column('hera_disk', 'public',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Disk.backing'
        db.delete_column('hera_disk', 'backing_id')

        # Deleting field 'Disk.created'
        db.delete_column('hera_disk', 'created')

        # Deleting field 'Disk.timeout'
        db.delete_column('hera_disk', 'timeout')


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
            'backing': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['hera.Disk']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['hera.Owner']"}),
            'refcount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timeout': ('django.db.models.fields.FloatField', [], {'default': '1e1000'})
        },
        'hera.owner': {
            'Meta': {'object_name': 'Owner'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hera.resourcerefreshed': {
            'Meta': {'object_name': 'ResourceRefreshed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'refreshes'", 'to': "orm['hera.DerivativeResource']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'})
        },
        'hera.template': {
            'Meta': {'object_name': 'Template'},
            'disk': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Disk']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '300'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['hera.Owner']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'hera.vm': {
            'Meta': {'object_name': 'VM'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vm_id': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['hera']
