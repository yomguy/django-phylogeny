import os

from django.test import TestCase

import phylogeny
from phylogeny.models import Taxon, TaxonomyDatabase, TaxonomyRecord, DistributionPoint
from phylogeny.exporters import PhyloXMLPhyloExporter, NexusPhyloExporter, NewickPhyloExporter
from phylogeny.exceptions import PhyloExporterUnsupportedTaxonAssignment


class GeneralPhylogenyTestCase(TestCase):
	'''Tests models and model fields.'''
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
	

class PhyloExporterTestCase(TestCase):
	'''Tests phylogeny exporters.'''
	fixtures = ('test-fixture-wasps.json',)
	
	def setUp(self):
		# querysets
		self.taxa = Taxon.objects.all()
		# instances
		self.first_taxon = self.taxa[0]
		# exporter
		self.phyloxml_exporter = PhyloXMLPhyloExporter(taxon=self.first_taxon, export_to='/export/')
		self.nexus_exporter = NexusPhyloExporter(taxon=self.first_taxon, export_to='/export/')
		self.newick_exporter = NewickPhyloExporter(taxon=self.first_taxon, export_to='/export/')
		# expected phyloxml
		phyloxml_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			phyloxml_path = os.path.join(phyloxml_path, path)
		phyloxml_path = os.path.join(phyloxml_path, 'tests', 'expected-phyloxml.xml')
		with open(phyloxml_path, 'r') as f:
			self.expected_phyloxml_string = f.read()
		# expected nexus
		nexus_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			nexus_path = os.path.join(nexus_path, path)
		nexus_path = os.path.join(nexus_path, 'tests', 'expected-nexus.nex')
		with open(nexus_path, 'r') as f:
			self.expected_nexus_string = f.read()
		# expected newick
		newick_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			newick_path = os.path.join(newick_path, path)
		newick_path = os.path.join(newick_path, 'tests', 'expected-newick.tree')
		with open(newick_path, 'r') as f:
			self.expected_newick_string = f.read()
	
	def testExporterExceptions(self):
		def phyloxml_taxon_assignment():
			self.phyloxml_exporter.taxon = 'taxon'
		def nexus_taxon_assignment():
			self.nexus_exporter.taxon = 'taxon'
		def newick_taxon_assignment():
			self.newick_exporter.taxon = 'taxon'
		
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, phyloxml_taxon_assignment)
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, nexus_taxon_assignment)
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, newick_taxon_assignment)
	
	def testTaxonAssignment(self):
		self.assertEqual(self.phyloxml_exporter.taxon, self.first_taxon)
		self.assertEqual(self.nexus_exporter.taxon, self.first_taxon)
		self.assertEqual(self.newick_exporter.taxon, self.first_taxon)
	
	def textExportToAssignment(self):
		self.assertEqual(self.phyloxml_exporter.export_to, '/export/')
		self.assertEqual(self.nexus_exporter.export_to, '/export/')
		self.assertEqual(self.newick_exporter.export_to, '/export/')
	
	def testXMLExporterOutput(self):
		self.assertEqual('%s' % self.phyloxml_exporter(), '%s' % self.expected_phyloxml_string)
		self.assertEqual('%s' % self.nexus_exporter(), '%s' % self.expected_nexus_string)
		self.assertEqual('%s' % self.newick_exporter(), '%s' % self.expected_newick_string)
	