# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VM'
        db.create_table('hera_vm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vm_id', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=120)),
        ))
        db.send_create_signal('hera', ['VM'])

        # Adding model 'DerivativeResource'
        db.create_table('hera_derivativeresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.Owner'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('timeout', self.gf('django.db.models.fields.FloatField')()),
            ('closed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('hera', ['DerivativeResource'])

        # Adding model 'ResourceRefreshed'
        db.create_table('hera_resourcerefreshed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='refreshes', to=orm['hera.DerivativeResource'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('hera', ['ResourceRefreshed'])

        # Adding model 'Owner'
        db.create_table('hera_owner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hera', ['Owner'])


    def backwards(self, orm):
        # Deleting model 'VM'
        db.delete_table('hera_vm')

        # Deleting model 'DerivativeResource'
        db.delete_table('hera_derivativeresource')

        # Deleting model 'ResourceRefreshed'
        db.delete_table('hera_resourcerefreshed')

        # Deleting model 'Owner'
        db.delete_table('hera_owner')


    models = {
        'hera.derivativeresource': {
            'Meta': {'object_name': 'DerivativeResource'},
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Owner']"}),
            'timeout': ('django.db.models.fields.FloatField', [], {})
        },
        'hera.owner': {
            'Meta': {'object_name': 'Owner'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hera.resourcerefreshed': {
            'Meta': {'object_name': 'ResourceRefreshed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'refreshes'", 'to': "orm['hera.DerivativeResource']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'hera.vm': {
            'Meta': {'object_name': 'VM'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vm_id': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['hera']