# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Taxon'
        db.create_table('phylogeny_taxon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('rank', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('year_of_description', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('common_name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('tagline', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.TaxaCategory'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ecology', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('distribution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('appearance_date_min_value', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('appearance_date_max_value', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('appearance_date_unit', self.gf('django.db.models.fields.CharField')(default='mya', max_length=3, blank=True)),
            ('appearance_date_annotation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('body_length_value', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('body_length_unit', self.gf('django.db.models.fields.CharField')(default='mm', max_length=2, blank=True)),
            ('social_unit_type', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('social_unit_size_min', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('social_unit_size_max', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('social_unit_annotation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('branch_length', self.gf('django.db.models.fields.FloatField')(default=1.0, null=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['phylogeny.Taxon'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('phylogeny', ['Taxon'])

        # Adding model 'Citation'
        db.create_table('phylogeny_citation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=512, blank=True)),
            ('doi', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('taxon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.Taxon'])),
        ))
        db.send_create_signal('phylogeny', ['Citation'])

        # Adding model 'TaxonomyDatabase'
        db.create_table('phylogeny_taxonomydatabase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=512)),
        ))
        db.send_create_signal('phylogeny', ['TaxonomyDatabase'])

        # Adding model 'TaxonomyRecord'
        db.create_table('phylogeny_taxonomyrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('taxon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.Taxon'])),
            ('database', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.TaxonomyDatabase'])),
            ('record_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=512, blank=True)),
        ))
        db.send_create_signal('phylogeny', ['TaxonomyRecord'])

        # Adding unique constraint on 'TaxonomyRecord', fields ['taxon', 'database', 'record_id']
        db.create_unique('phylogeny_taxonomyrecord', ['taxon_id', 'database_id', 'record_id'])

        # Adding model 'DistributionPoint'
        db.create_table('phylogeny_distributionpoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('taxon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.Taxon'])),
        ))
        db.send_create_signal('phylogeny', ['DistributionPoint'])

        # Adding unique constraint on 'DistributionPoint', fields ['latitude', 'longitude', 'taxon']
        db.create_unique('phylogeny_distributionpoint', ['latitude', 'longitude', 'taxon_id'])

        # Adding model 'TaxonImageCategory'
        db.create_table('phylogeny_taxonimagecategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('phylogeny', ['TaxonImageCategory'])

        # Adding model 'TaxonImage'
        db.create_table('phylogeny_taxonimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.TaxonImageCategory'], null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('taxon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phylogeny.Taxon'])),
        ))
        db.send_create_signal('phylogeny', ['TaxonImage'])

        # Adding model 'TaxaCategory'
        db.create_table('phylogeny_taxacategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=7)),
        ))
        db.send_create_signal('phylogeny', ['TaxaCategory'])


    def backwards(self, orm):
        # Removing unique constraint on 'DistributionPoint', fields ['latitude', 'longitude', 'taxon']
        db.delete_unique('phylogeny_distributionpoint', ['latitude', 'longitude', 'taxon_id'])

        # Removing unique constraint on 'TaxonomyRecord', fields ['taxon', 'database', 'record_id']
        db.delete_unique('phylogeny_taxonomyrecord', ['taxon_id', 'database_id', 'record_id'])

        # Deleting model 'Taxon'
        db.delete_table('phylogeny_taxon')

        # Deleting model 'Citation'
        db.delete_table('phylogeny_citation')

        # Deleting model 'TaxonomyDatabase'
        db.delete_table('phylogeny_taxonomydatabase')

        # Deleting model 'TaxonomyRecord'
        db.delete_table('phylogeny_taxonomyrecord')

        # Deleting model 'DistributionPoint'
        db.delete_table('phylogeny_distributionpoint')

        # Deleting model 'TaxonImageCategory'
        db.delete_table('phylogeny_taxonimagecategory')

        # Deleting model 'TaxonImage'
        db.delete_table('phylogeny_taxonimage')

        # Deleting model 'TaxaCategory'
        db.delete_table('phylogeny_taxacategory')


    models = {
        'phylogeny.citation': {
            'Meta': {'object_name': 'Citation'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'doi': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'taxon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.Taxon']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '512', 'blank': 'True'})
        },
        'phylogeny.distributionpoint': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'taxon'),)", 'object_name': 'DistributionPoint'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'place_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'taxon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.Taxon']"})
        },
        'phylogeny.taxacategory': {
            'Meta': {'object_name': 'TaxaCategory'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'phylogeny.taxon': {
            'Meta': {'object_name': 'Taxon'},
            'appearance_date_annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'appearance_date_max_value': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'appearance_date_min_value': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'appearance_date_unit': ('django.db.models.fields.CharField', [], {'default': "'mya'", 'max_length': '3', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'body_length_unit': ('django.db.models.fields.CharField', [], {'default': "'mm'", 'max_length': '2', 'blank': 'True'}),
            'body_length_value': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'branch_length': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.TaxaCategory']", 'null': 'True', 'blank': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distribution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ecology': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['phylogeny.Taxon']"}),
            'rank': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'social_unit_annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'social_unit_size_max': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'social_unit_size_min': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'social_unit_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'year_of_description': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'phylogeny.taxonimage': {
            'Meta': {'object_name': 'TaxonImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.TaxonImageCategory']", 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'taxon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.Taxon']"}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'phylogeny.taxonimagecategory': {
            'Meta': {'object_name': 'TaxonImageCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'phylogeny.taxonomydatabase': {
            'Meta': {'object_name': 'TaxonomyDatabase'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '512'})
        },
        'phylogeny.taxonomyrecord': {
            'Meta': {'unique_together': "(('taxon', 'database', 'record_id'),)", 'object_name': 'TaxonomyRecord'},
            'database': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.TaxonomyDatabase']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'taxon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phylogeny.Taxon']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '512', 'blank': 'True'})
        }
    }

    complete_apps = ['phylogeny']