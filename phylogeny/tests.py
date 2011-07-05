from django.test import TestCase

from phylogeny.models import Taxon, TaxonomyDatabase, TaxonomyRecord, DistributionPoint


class WaspsPhylogenyTestCase(TestCase):
	'''
	Tests models and model fields.
	'''
	fixtures = ('test-fixture-wasps.json',)
	
	def setUp(self):
		# querysets
		self.taxa = Taxon.objects.all()
		self.taxonomy_databases = TaxonomyDatabase.objects.all()
		self.taxonomy_records = TaxonomyRecord.objects.all()
		self.distribution_points = DistributionPoint.objects.all()
		# instances
		self.first_taxon = self.taxa[0]
		self.last_taxon = self.taxa.reverse()[0]
	
	def testDepthFirstOrdering(self):
		self.assertTrue(self.first_taxon.is_root_node())
		self.assertTrue(self.last_taxon.is_leaf_node())
		self.assertEqual(self.first_taxon.name, 'Animalia')
		self.assertEqual(self.last_taxon.name, 'Vespa crabro')
	
	def testCitations(self):
		self.assertEqual(self.first_taxon.citation_set.count(), 1)
		self.assertEqual(self.last_taxon.citation_set.count(), 1)
	
	def testTaxonomies(self):
		for taxon in self.taxa:
			self.assertEqual(taxon.taxonomyrecord_set.count(), 1)
			self.assertEqual(taxon.taxonomyrecord_set.get().database.name, 'ITIS')
	
	def testDistributions(self):
		self.assertEqual(self.first_taxon.distributionpoint_set.count(), 1)
		self.assertEqual(self.last_taxon.distributionpoint_set.count(), 0)
		self.assertEqual(self.first_taxon.distributionpoint_set.get().place_name, 'worldwide')
		self.assertEqual(self.first_taxon.distributionpoint_set.get().latitude, 1)
		self.assertEqual(self.first_taxon.distributionpoint_set.get().longitude, -1)
	
	def testNaturalKeys(self):
		for taxon in self.taxa:
			self.assertEqual(Taxon.objects.get_by_natural_key(*taxon.natural_key()), taxon)
		for taxonomy_database in self.taxonomy_databases:
			self.assertEqual(TaxonomyDatabase.objects.get_by_natural_key(*taxonomy_database.natural_key()), taxonomy_database)
		for taxonomy_record in self.taxonomy_records:
			self.assertEqual(TaxonomyRecord.objects.get_by_natural_key(*taxonomy_record.natural_key()), taxonomy_record)
		for distribution_point in self.distribution_points:
			self.assertEqual(DistributionPoint.objects.get_by_natural_key(*distribution_point.natural_key()), distribution_point)

