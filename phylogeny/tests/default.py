import os

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

import phylogeny
from phylogeny.models import Taxon, TaxonomyDatabase, TaxonomyRecord, DistributionPoint
from phylogeny.exporters import exporter_registry, PhyloXMLPhyloExporter, NexusPhyloExporter, NewickPhyloExporter, JSPhyloSVGPhyloXMLPhyloExporter
from phylogeny.importers import importer_registry, PhyloXMLPhyloImporter, NexusPhyloImporter, NewickPhyloImporter
from phylogeny.exceptions import PhyloExporterUnsupportedTaxonAssignment, PhyloExporterRegistryOnlyClassesMayRegister, PhyloExporterRegistryClassAlreadyRegistered, PhyloExporterRegistryExporterNotFound, PhyloImporterRegistryOnlyClassesMayRegister, PhyloImporterRegistryClassAlreadyRegistered, PhyloImporterRegistryImporterNotFound, PhylogenyImportMergeConflict


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
		self.js_phylo_exporter = JSPhyloSVGPhyloXMLPhyloExporter(taxon=self.first_taxon, export_to='/export/')
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
		# expected js phylo
		js_phylo_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			js_phylo_path = os.path.join(js_phylo_path, path)
		js_phylo_path = os.path.join(js_phylo_path, 'tests', 'expected-phyloxml-jsphylosvg.xml')
		with open(js_phylo_path, 'r') as f:
			self.expected_js_phylo_string = f.read()
	
	def testExporterExceptions(self):
		def phyloxml_taxon_assignment():
			self.phyloxml_exporter.taxon = 'taxon'
		def nexus_taxon_assignment():
			self.nexus_exporter.taxon = 'taxon'
		def newick_taxon_assignment():
			self.newick_exporter.taxon = 'taxon'
		def js_phylo_taxon_assignment():
			self.js_phylo_exporter.taxon = 'taxon'
		
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, phyloxml_taxon_assignment)
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, nexus_taxon_assignment)
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, newick_taxon_assignment)
		self.assertRaises(PhyloExporterUnsupportedTaxonAssignment, js_phylo_taxon_assignment)
	
	def testTaxonAssignment(self):
		self.assertEqual(self.phyloxml_exporter.taxon, self.first_taxon)
		self.assertEqual(self.nexus_exporter.taxon, self.first_taxon)
		self.assertEqual(self.newick_exporter.taxon, self.first_taxon)
		self.assertEqual(self.js_phylo_exporter.taxon, self.first_taxon)
	
	def testExportToAssignment(self):
		self.assertEqual(self.phyloxml_exporter.export_to, '/export/')
		self.assertEqual(self.nexus_exporter.export_to, '/export/')
		self.assertEqual(self.newick_exporter.export_to, '/export/')
		self.assertEqual(self.js_phylo_exporter.export_to, '/export/')
	
	def testXMLExporterOutput(self):
		self.assertEqual('%s' % self.phyloxml_exporter(), '%s' % self.expected_phyloxml_string)
		self.assertEqual('%s' % self.nexus_exporter(), '%s' % self.expected_nexus_string)
		self.assertEqual('%s' % self.newick_exporter(), '%s' % self.expected_newick_string)
		self.assertEqual('%s' % self.js_phylo_exporter(), '%s' % self.expected_js_phylo_string)
	

class PhyloExporterRegistryTestCase(TestCase):
	'''Tests phylogeny exporter registry.'''
	def setUp(self):
		self.exporter_registry = exporter_registry
	
	def testExporterRegistryExceptions(self):
		def register_non_class():
			self.exporter_registry.register('string')
		def register_class_twice():
			self.exporter_registry.register(PhyloXMLPhyloExporter)
		def get_bad_format_name():
			self.exporter_registry.get_by_format_name('string')
		def get_bad_extension():
			self.exporter_registry.get_by_extension('string')
		
		self.assertRaises(PhyloExporterRegistryOnlyClassesMayRegister, register_non_class)
		self.assertRaises(PhyloExporterRegistryClassAlreadyRegistered, register_class_twice)
		self.assertRaises(PhyloExporterRegistryExporterNotFound, get_bad_format_name)
		self.assertRaises(PhyloExporterRegistryExporterNotFound, get_bad_extension)
	

class PhyloImporterTestCase(TestCase):
	'''Tests phylogeny importers.'''
	
	def setUp(self):
		# exporter
		self.phyloxml_importer = PhyloXMLPhyloImporter()
		self.nexus_importer = NexusPhyloImporter()
		self.newick_importer = NewickPhyloImporter()
		# expected phyloxml
		phyloxml_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			phyloxml_path = os.path.join(phyloxml_path, path)
		self.phyloxml_path = os.path.join(phyloxml_path, 'tests', 'expected-phyloxml.xml')
		# expected nexus
		nexus_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			nexus_path = os.path.join(nexus_path, path)
		self.nexus_path = os.path.join(nexus_path, 'tests', 'expected-nexus.nex')
		# expected newick
		newick_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			newick_path = os.path.join(newick_path, path)
		self.newick_path = os.path.join(newick_path, 'tests', 'expected-newick.tree')
	
	def testPhyloXMLImport(self):
		self.phyloxml_importer.import_from = self.phyloxml_path
		self.phyloxml_importer.save()
		self.assertEqual(Taxon.objects.count(), 13)
	
	def testNexusImport(self):
		self.nexus_importer.import_from = self.nexus_path
		self.nexus_importer.save()
		self.assertEqual(Taxon.objects.count(), 13)
	
	def testNewickImport(self):
		self.newick_importer.import_from = self.newick_path
		self.newick_importer.save()
		self.assertEqual(Taxon.objects.count(), 13)
	

class PhyloImporterRegistryTestCase(TestCase):
	'''Tests phylogeny importer registry.'''
	fixtures = ('test-fixture-wasps.json',)
	
	def setUp(self):
		self.importer_registry = importer_registry
		# expected phyloxml
		phyloxml_path = ''
		phylogeny_path = phylogeny.__path__
		for path in phylogeny_path:
			phyloxml_path = os.path.join(phyloxml_path, path)
		self.phyloxml_path = os.path.join(phyloxml_path, 'tests', 'expected-phyloxml.xml')
	
	def testImporterRegistryExceptions(self):
		def register_non_class():
			self.importer_registry.register('string')
		def register_class_twice():
			self.importer_registry.register(PhyloXMLPhyloImporter)
		def get_bad_format_name():
			self.importer_registry.get_by_format_name('string')
		def import_conflict():
			importer = PhyloXMLPhyloImporter(import_from=self.phyloxml_path)
			importer.save()
		
		self.assertRaises(PhyloImporterRegistryOnlyClassesMayRegister, register_non_class)
		self.assertRaises(PhyloImporterRegistryClassAlreadyRegistered, register_class_twice)
		self.assertRaises(PhyloImporterRegistryImporterNotFound, get_bad_format_name)
		self.assertRaises(PhylogenyImportMergeConflict, import_conflict)
	
