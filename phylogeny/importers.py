from abc import ABCMeta, abstractmethod, abstractproperty
from inspect import isclass

from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from Bio import Phylo

from phylogeny.models import Taxon, Citation, TaxonomyDatabase, TaxonomyRecord, DistributionPoint
from phylogeny.exceptions import PhyloImporterRegistryOnlyClassesMayRegister, PhyloImporterRegistryClassAlreadyRegistered, PhyloImporterRegistryImporterNotFound
from phylogeny.utils import slugify_unique


class ImporterRegistry(object):
	'''
	Registers importers and reports on importer availability.
	
	Importer classes may register with a Registry instance:
		`importer_registry.register(ImporterClass)`
	'''
	def __init__(self):
		self._registry = set()
	
	def register(self, importer_class):
		'''Register an importer class.'''
		if not isclass(importer_class):
			raise PhyloImporterRegistryOnlyClassesMayRegister(ugettext('Only classes may register with the importer registry.  %s is not a class.') % importer_class)
		if importer_class in self._registry:
			raise PhyloImporterRegistryClassAlreadyRegistered(ugettext('Importer classes may register only once.  %s is alredy registered.') % importer_class)
		
		# instantiate importer class so as to raise any errors which would
		# otherwise appear only upon later instantiation
		importer_class()
		
		self._registry.add(importer_class)
	
	def get_importers(self):
		'''
		Returns a tuple of registered importer instances.
		'''
		importers = tuple(importer_class for importer_class in self._registry)
		return importers
	
	def get_by_format_name(self, format_name):
		'''
		Returns an instance of the first importer with a matching format name.
		'''
		for importer_class in self._registry:
			if importer_class.format_name == format_name:
				return importer_class()
		raise PhyloImporterRegistryImporterNotFound(ugettext('Importer with format name %s not found.') % format_name)
	

class AbstractBasePhyloImporter(object):
	'''
	Provides base functionality and method stubs for phylogeny importers.
	Subclasses must implement methods marked as abstract methods.
	'''
	__metaclass__ = ABCMeta
	# name of importer
	verbose_name = _('Import Phylogeny')
	# name of phylogeny format
	format_name = None
	
	def __init__(self, phylogeny=None, import_from=None):
		'''Initializes an instance of the phylogeny importer.'''
		self.phylogeny = phylogeny
		self.import_from = import_from
		
		if self.format_name is None:
			raise PhyloImporterMissingAttrbute(ugettext('Importer %s missing `format_name`.') % self)
		
		return super(AbstractBasePhyloImporter, self).__init__()
	
	def __repr__(self):
		'''Returns the unicode representation of an importer instance.'''
		try:
			u = unicode(self)
		except (UnicodeEncodeError, UnicodeDecodeError):
			u = '[Bad Unicode data]'
		return u'<%s: %s>' % (self.__class__.__name__, u)
	
	def __unicode__(self):
		'''Returns a unicode string of an import instance's verbose name.'''
		if self.phylogeny:
			return u'%s' % self.phylogeny
		return u'%s' % self.verbose_name
	
	@property
	def phylogeny(self):
		'''
		A phylogeny object associated with the importer.  Raises
		PhyloImporterPhyloenyNotProvided error if no phylogeny was provied.
		'''
		return self._phylogeny
	
	@phylogeny.setter
	def phylogeny(self, phylogeny):
		'''
		Sets the value of the `phylogeny` property.
		'''
		self._phylogeny = phylogeny
	
	@property
	def import_from(self):
		'''
		The path where the importer should get the phylogeny when using
		the `save` method.
		'''
		import_from = None
		if callable(self._import_from):
			import_from = '%s' % self._import_from()
		elif self._import_from:
			import_from = '%s' % self._import_from
		return import_from
	
	@import_from.setter
	def import_from(self, import_from):
		'''Sets the value of the `import_from` property.'''
		if import_from is not None:
			self._import_from = import_from
			self.phylogeny = Phylo.read(self.import_from, self.format_name)
	
	@abstractmethod
	def get_object(self):
		'''Returns a Taxon representating the phylogeny to import.'''
		pass
	
	@abstractmethod
	def save(self):
		'''Saves the taxon to the database.'''
		pass
	

class AbstractBaseBiopythonPhyloImporter(AbstractBasePhyloImporter):
	'''Imports a phylogeny rooted on a given taxon to a Biopython phylogeny.'''
	__metaclass__ = ABCMeta
	verbose_name = _('Import Biopython Phylogeny')
	
	def get_taxon_for_clade(self, clade, parent_taxon=None):
		'''
		Imports data from a phylogeny and saves taxa to the database.

		Merge conflicts can arise when an imported clade's name matches an existing
		taxon's name.  In the case of conflicts, a merge strategy is used.  The
		default merge strategy is to abort import.
		
		Always use an importer's `save` method to ensure database changes are
		run in transaction and rolled back in the event of a conflict.

		Available merge strategies are:

			None:  the default merge strategy is to abort import.
		'''

		# merge strategy None is the only supported strategy at this time
		merge_strategy = None
		
		# base name
		taxon_name = clade.name or 'none'
		# sometimes the name can be in a taxonomy, but not the clade itself
		if hasattr(clade, 'taxonomies') and len(clade.taxonomies) > 0 and hasattr(clade.taxonomies[0], 'scientific_name'):
			taxon_name = clade.taxonomies[0].scientific_name or taxon_name

		defaults = {
			'name': taxon_name,
			'slug': slugify_unique(taxon_name, Taxon),
			'branch_length': 1.0
		}

		if hasattr(clade, 'branch_length'):
			defaults['branch_length'] = clade.branch_length

		# add clade date to taxon defaults if available
		# NOTE:  date output is disabled since Biopython can't read its own output
		# that contains dates
		#if hasattr(clade, 'date'):
		#	if hasattr(clade.date, 'unit'):
		#		defaults['appearance_date_unit'] = clade.date.unit
		#	if hasattr(clade.date, 'desc'):
		#		defaults['appearance_date_annotation'] = clade.date.desc
		#	if hasattr(clade.date, 'minimum'):
		#		defaults['appearance_date_min_value'] = clade.date.minimum
		#	if hasattr(clade.date, 'maximum'):
		#		defaults['appearance_date_max_value'] = clade.date.maximum

		# get or create a taxon matching taxon_name
		lookup_slug = slugify(taxon_name)
		if taxon_name == 'none':
			lookup_slug = slugify_unique(taxon_name, Taxon)

		taxon, created = Taxon.objects.get_or_create(slug=lookup_slug, defaults=defaults)

		# None merge strategy
		if merge_strategy is None and not created:
			# merge strategy is None or other:
			raise PhylogenyImportMergeConflict(ugettext('Merge conflict occurred:  name "%(taxon_name)s" already exists.  Import aborted.  This may be caused by two clades having the same name in the phylogeny file or by a clade having the same name as an existing taxon.  Please change the name of the existing taxon or change the name of the taxon in the import file.') % {'taxon_name': taxon.name})

		if created:
			taxon.save()
			# import taxonomies, distributions, and references
			if hasattr(clade, 'taxonomies'):
				for taxonomy in clade.taxonomies:
					if taxonomy.id and taxonomy.id.value and taxonomy.id.provider:
						taxonomy_database_slug = slugify(taxonomy.id.provider)
						taxonomy_database, c = TaxonomyDatabase.objects.get_or_create(name=taxonomy.id.provider, slug=taxonomy_database_slug)
						taxonomy_record, c = TaxonomyRecord.objects.get_or_create(taxon=taxon, database=taxonomy_database, record_id=taxonomy.id.value)
			if hasattr(clade, 'distributions'):
				for distribution in clade.distributions:
					if distribution.desc and not distribution.points:
						taxon.distribution = u'%s %s' % (distribution.desc, taxon.distribution)
					for point in distribution.points:
						distribution_point = DistributionPoint.objects.create(taxon=taxon, place_name=distribution.desc or '', latitude=point.lat, longitude=point.long)
			if hasattr(clade, 'references'):
				for reference in clade.references:
					citation = Citation.objects.create(taxon=taxon, description=reference.desc or '', doi=reference.doi or '')

		# move taxon to parent (or root if no parent)
		taxon.move_to(parent_taxon)

		for child_clade in clade.clades:
			self.get_taxon_for_clade(child_clade, parent_taxon=taxon)

		return taxon
	
	def get_object(self):
		'''Returns a Taxon model instance for the imported phylogeny.'''
		taxon = self.get_taxon_for_clade(self.phylogeny.root)
		return taxon
	
	def save(self, import_from=None):
		'''
		Saves the phylogeny to the database in a transaction.  If a merge
		conflict occurs, the transaction is rolled back.
		'''
		if import_from is not None:
			self.import_from = import_from
		
		with transaction.commit_on_success():
			# start transaction
			taxon = self.get_object()
			taxon.save()
	

class PhyloXMLPhyloImporter(AbstractBaseBiopythonPhyloImporter):
	'''Imports a phylogeny from a Biopython PhyloXML phylogeny file.'''
	verbose_name = _('Import PhyloXML Phylogeny')
	format_name = 'phyloxml'


class NexusPhyloImporter(AbstractBaseBiopythonPhyloImporter):
	'''Imports a phylogeny from a Biopython Nexus phylogeny file.'''
	verbose_name = _('Import Nexus Phylogeny')
	format_name = 'nexus'


class NewickPhyloImporter(AbstractBaseBiopythonPhyloImporter):
	'''Imports a phylogeny from a Biopython Newick phylogeny file.'''
	verbose_name = _('Import Newick Phylogeny')
	format_name = 'newick'


# registry is used to register importer classes and report on them
# throughout the app
importer_registry = ImporterRegistry()
# register concrete importer classes
importer_registry.register(PhyloXMLPhyloImporter)
importer_registry.register(NexusPhyloImporter)
importer_registry.register(NewickPhyloImporter)
