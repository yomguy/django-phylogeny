from django.db.models import Manager

from mptt import managers as mptt_managers


class TaxonManager(mptt_managers.TreeManager):
	def get_by_natural_key(self, slug):
		return self.get(slug=slug)


class TaxonomyDatabaseManager(Manager):
	def get_by_natural_key(self, slug):
		return self.get(slug=slug)


class TaxonomyRecordManager(Manager):
	def get_by_natural_key(self, record_id, database_slug, taxon_slug):
		from phylogeny.models import Taxon, TaxonomyDatabase
		return self.get(record_id=record_id, database=TaxonomyDatabase.objects.get_by_natural_key(database_slug), taxon=Taxon.objects.get_by_natural_key(taxon_slug))


class DistributionPointManager(Manager):
	def get_by_natural_key(self, latitude, longitude, taxon_slug):
		from phylogeny.models import Taxon
		return self.get(latitude=latitude, longitude=longitude, taxon=Taxon.objects.get_by_natural_key(taxon_slug))


class ColorManager(Manager):
	def get_by_natural_key(self, slug):
		return self.get(slug=slug)


class TaxonBackgroundColorManager(Manager):
	def get_by_natural_key(self, color_slug, taxon_slug):
		from phylogeny.models import Taxon, Color
		return self.get(color=Color.objects.get_by_natural_key(color_slug), taxon=Taxon.objects.get_by_natural_key(taxon_slug))
