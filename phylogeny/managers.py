from django.db.models import Manager

from mptt import managers as mptt_managers


class TaxonManager(mptt_managers.TreeManager):
	def get_by_natural_key(self, slug,):
		return self.get(slug=slug)


class CitationManager(Manager):
	def get_by_natural_key(self, description,):
		return self.get(description=description)


class TaxonomyDatabaseManager(Manager):
	def get_by_natural_key(self, slug,):
		return self.get(slug=slug)


class TaxonomyRecordManager(Manager):
	def get_by_natural_key(self, record_id, database_slug):
		from phylogeny.models import TaxonomyDatabase
		return self.get(record_id=record_id, database=TaxonomyDatabase.objects.get_by_natural_key(database_slug))


class DistributionPointManager(Manager):
	def get_by_natural_key(self, place_name, latitude, longitude, taxon_slug):
		from phylogeny.models import Taxon
		return self.get(place_name=place_name, latitude=latitude, longitude=longitude, taxon=Taxon.objects.get_by_natural_key(taxon_slug))


class TaxonImageCategoryManager(Manager):
	def get_by_natural_key(self, slug,):
		return self.get(slug=slug)


class TaxonImageManager(Manager):
	def get_by_natural_key(self, caption,):
		return self.get(caption=caption)
