# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ImageMapItem'
        db.delete_table(u'activities_imagemapitem')

        # Deleting model 'ImageMapChart'
        db.delete_table(u'activities_imagemapchart')

        # Removing M2M table for field items on 'ImageMapChart'
        db.delete_table(db.shorten_name(u'activities_imagemapchart_items'))

        # Adding model 'ImageInteractive'
        db.create_table(u'activities_imageinteractive', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('intro_text', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'activities', ['ImageInteractive'])

        # Adding field 'CalendarChart.appointment'
        db.add_column(u'activities_calendarchart', 'appointment',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'ImageMapItem'
        db.create_table(u'activities_imagemapitem', (
            ('map_area_shape', self.gf('django.db.models.fields.CharField')(default='', max_length=64)),
            ('coordinates', self.gf('django.db.models.fields.TextField')()),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('label_name', self.gf('django.db.models.fields.CharField')(default='', max_length=64)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'activities', ['ImageMapItem'])

        # Adding model 'ImageMapChart'
        db.create_table(u'activities_imagemapchart', (
            ('intro_text', self.gf('django.db.models.fields.TextField')(default='')),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'activities', ['ImageMapChart'])

        # Adding M2M table for field items on 'ImageMapChart'
        m2m_table_name = db.shorten_name(u'activities_imagemapchart_items')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('imagemapchart', models.ForeignKey(orm[u'activities.imagemapchart'], null=False)),
            ('imagemapitem', models.ForeignKey(orm[u'activities.imagemapitem'], null=False))
        ))
        db.create_unique(m2m_table_name, ['imagemapchart_id', 'imagemapitem_id'])

        # Deleting model 'ImageInteractive'
        db.delete_table(u'activities_imageinteractive')

        # Deleting field 'CalendarChart.appointment'
        db.delete_column(u'activities_calendarchart', 'appointment')


    models = {
        u'activities.calendarchart': {
            'Meta': {'object_name': 'CalendarChart'},
            'appointment': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'birth_date': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.calendarresponse': {
            'Meta': {'object_name': 'CalendarResponse'},
            'conv_scen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.CalendarChart']", 'null': 'True', 'blank': 'True'}),
            'first_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_first_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_last_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'activities.convclick': {
            'Meta': {'object_name': 'ConvClick'},
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.Conversation']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.conversation': {
            'Meta': {'object_name': 'Conversation'},
            'complete_dialog': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'response_three': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'response_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'scenario_type': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'}),
            'text_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'activities.conversationresponse': {
            'Meta': {'object_name': 'ConversationResponse'},
            'conv_scen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activities.ConversationScenario']", 'null': 'True', 'blank': 'True'}),
            'first_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'first_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'second_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'third_click': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'third_click'", 'null': 'True', 'to': u"orm['activities.ConvClick']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'activities.conversationscenario': {
            'Meta': {'object_name': 'ConversationScenario'},
            'bad_conversation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bad_conversation'", 'null': 'True', 'to': u"orm['activities.Conversation']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'good_conversation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'good_conversation'", 'null': 'True', 'to': u"orm['activities.Conversation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'activities.dosageactivity': {
            'Meta': {'object_name': 'DosageActivity'},
            'explanation': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ml_nvp': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'times_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weeks': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'activities.dosageactivityresponse': {
            'Meta': {'object_name': 'DosageActivityResponse'},
            'dosage_activity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dosage_resp'", 'null': 'True', 'to': u"orm['activities.DosageActivity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ml_nvp': ('django.db.models.fields.IntegerField', [], {}),
            'times_day': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'weeks': ('django.db.models.fields.IntegerField', [], {})
        },
        u'activities.imageinteractive': {
            'Meta': {'object_name': 'ImageInteractive'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pagetree.hierarchy': {
            'Meta': {'object_name': 'Hierarchy'},
            'base_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'pagetree.pageblock': {
            'Meta': {'ordering': "('section', 'ordinality')", 'object_name': 'PageBlock'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'css_extra': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ordinality': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Section']"})
        },
        u'pagetree.section': {
            'Meta': {'object_name': 'Section'},
            'deep_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hierarchy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Hierarchy']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['activities']
