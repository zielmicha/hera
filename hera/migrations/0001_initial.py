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
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.Account'])),
            ('stats', self.gf('jsonfield.fields.JSONField')()),
            ('vm_id', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=120)),
        ))
        db.send_create_signal('hera', ['VM'])

        # Adding model 'DerivativeResource'
        db.create_table('hera_derivativeresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.Account'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expiry', self.gf('django.db.models.fields.DateTimeField')()),
            ('closed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('base_prize_per_second', self.gf('django.db.models.fields.FloatField')()),
            ('custom', self.gf('jsonfield.fields.JSONField')()),
            ('user_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('hera', ['DerivativeResource'])

        # Adding model 'DerivativeResourceUsed'
        db.create_table('hera_derivativeresourceused', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.DerivativeResource'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('prize', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('hera', ['DerivativeResourceUsed'])

        # Adding model 'Account'
        db.create_table('hera_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('billing_owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_main', self.gf('django.db.models.fields.BooleanField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('prize_per_second_limit', self.gf('django.db.models.fields.FloatField')()),
            ('prize_used', self.gf('django.db.models.fields.FloatField')()),
            ('prize_transferred_to', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('hera', ['Account'])

        # Adding model 'Disk'
        db.create_table('hera_disk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, to=orm['hera.Account'])),
            ('refcount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('backing', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, to=orm['hera.Disk'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('timeout', self.gf('django.db.models.fields.FloatField')(default=1e+100)),
        ))
        db.send_create_signal('hera', ['Disk'])

        # Adding model 'Template'
        db.create_table('hera_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, to=orm['hera.Account'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hera.Disk'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal('hera', ['Template'])


    def backwards(self, orm):
        # Deleting model 'VM'
        db.delete_table('hera_vm')

        # Deleting model 'DerivativeResource'
        db.delete_table('hera_derivativeresource')

        # Deleting model 'DerivativeResourceUsed'
        db.delete_table('hera_derivativeresourceused')

        # Deleting model 'Account'
        db.delete_table('hera_account')

        # Deleting model 'Disk'
        db.delete_table('hera_disk')

        # Deleting model 'Template'
        db.delete_table('hera_template')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'", 'object_name': 'ContentType', 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hera.account': {
            'Meta': {'object_name': 'Account'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'billing_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'prize_per_second_limit': ('django.db.models.fields.FloatField', [], {}),
            'prize_transferred_to': ('django.db.models.fields.FloatField', [], {}),
            'prize_used': ('django.db.models.fields.FloatField', [], {})
        },
        'hera.derivativeresource': {
            'Meta': {'object_name': 'DerivativeResource'},
            'base_prize_per_second': ('django.db.models.fields.FloatField', [], {}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom': ('jsonfield.fields.JSONField', [], {}),
            'expiry': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Account']"}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hera.derivativeresourceused': {
            'Meta': {'object_name': 'DerivativeResourceUsed'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prize': ('django.db.models.fields.FloatField', [], {}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.DerivativeResource']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'hera.disk': {
            'Meta': {'object_name': 'Disk'},
            'backing': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['hera.Disk']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['hera.Account']"}),
            'refcount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timeout': ('django.db.models.fields.FloatField', [], {'default': '1e+100'})
        },
        'hera.template': {
            'Meta': {'object_name': 'Template'},
            'disk': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Disk']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['hera.Account']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'hera.vm': {
            'Meta': {'object_name': 'VM'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hera.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stats': ('jsonfield.fields.JSONField', [], {}),
            'vm_id': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['hera']