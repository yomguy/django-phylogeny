'''
Managers to Phylogeny models.
'''
from django.db.models import Manager

from mptt import managers as mptt_managers


class TaxonManager(mptt_managers.TreeManager):
	'''Manager for Taxon model.'''
	def get_by_natural_key(self, slug):
		'''Returns taxon instance with matching slug.'''
		return self.get(slug=slug)


class TaxonomyDatabaseManager(Manager):
	'''Manager for TaxonomyDatabase model.'''
	def get_by_natural_key(self, slug):
		'''Returns taxonomy database instance with matching slug.'''
		return self.get(slug=slug)


class TaxonomyRecordManager(Manager):
	'''Manager for TaxonomyRecord model.'''
	def get_by_natural_key(self, record_id, database_slug, taxon_slug):
		'''
		Returns taxnomy record instance with matching record_id, databse,
		and taxon.
		'''
		from phylogeny.models import Taxon, TaxonomyDatabase
		return self.get(record_id=record_id, database=TaxonomyDatabase.objects.get_by_natural_key(database_slug), taxon=Taxon.objects.get_by_natural_key(taxon_slug))


class DistributionPointManager(Manager):
	'''Manager for DistributionPoint model.'''
	def get_by_natural_key(self, latitude, longitude, taxon_slug):
		'''
		Returns distribution point instancewith matching lat/long and taxon.
		'''
		from phylogeny.models import Taxon
		return self.get(latitude=latitude, longitude=longitude, taxon=Taxon.objects.get_by_natural_key(taxon_slug))


class TaxaCategoryManager(Manager):
	'''Manager for TaxaCategory model.'''
	def get_by_natural_key(self, slug):
		'''Returns taxa category with matching slug.'''
		return self.get(slug=slug)
