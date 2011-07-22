'''
Phylogeny exporters output a phylogeny format (such as Nexus or PhyloXML) rooted
on a given Taxon instance.

Exporter classes must be based on the ABC AbstractBasePhyloExporter.  Exporters
should register with the exporter registry to make themselves known and
accessible throughout the app:

	exporter_registry.register(<MyExporterClass>)
'''
from abc import ABCMeta, abstractmethod
from inspect import isclass

from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from Bio import Phylo

from phylogeny.models import Taxon, TaxaCategory
from phylogeny.exceptions import PhyloExporterUnsupportedTaxonAssignment, PhyloExporterMissingAttribute, PhyloExporterRegistryOnlyClassesMayRegister, PhyloExporterRegistryClassAlreadyRegistered, PhyloExporterRegistryExporterNotFound


class ExporterRegistry(object):
	'''
	Registers exporters and reports on exporter availability.
	
	Exporter classes may register with a Registry instance:
		`registry.register(ExporterClass)`
	'''
	def __init__(self):
		self._registry = set()
	
	def register(self, exporter_class):
		'''Register an exporter class.'''
		if not isclass(exporter_class):
			raise PhyloExporterRegistryOnlyClassesMayRegister(ugettext('Only classes may register with the exporter registry.  %s is not a class.') % exporter_class)
		if exporter_class in self._registry:
			raise PhyloExporterRegistryClassAlreadyRegistered(ugettext('Exporter classes may register only once.  %s is alredy registered.') % exporter_class)
		
		# instantiate exporter class so as to raise any errors which would
		# otherwise appear only upon later instantiation
		exporter_class()
		
		self._registry.add(exporter_class)
	
	def get_exporters(self):
		'''
		Returns a tuple of registered exporter instances.
		'''
		exporters = tuple(exporter_class for exporter_class in self._registry)
		return exporters
	
	def get_by_format_name(self, format_name):
		'''
		Returns an instance of the first exporter with a matching format name.
		'''
		for exporter_class in self._registry:
			if exporter_class.format_name == format_name:
				return exporter_class()
		raise PhyloExporterRegistryExporterNotFound(ugettext('Exporter with format name %s not found.') % format_name)
	
	def get_by_extension(self, extension):
		'''
		Returns an instance of the first exporter with a matching extension.
		'''
		for exporter_class in self._registry:
			if exporter_class.extension == extension:
				return exporter_class()
		raise PhyloExporterRegistryExporterNotFound(ugettext('Exporter with extension %s not found.') % extension)
	
	def get_by_format_and_extension(self, format_name, extension):
		'''
		Returns an instance of the first exporter with both a matching format
		name and extension.
		'''
		for exporter_class in self._registry:
			if exporter_class.format_name == format_name and exporter_class.extension == extension:
				return exporter_class()
		raise PhyloExporterRegistryExporterNotFound(ugettext('Exporter with format name %s and extension %s not found.') % (format_name, extension,))


class AbstractBasePhyloExporter(object):
	'''
	Provides base functionality and method stubs for phylogeny exporters.
	Subclasses must implement methods marked as abstract methods.
	'''
	__metaclass__ = ABCMeta
	# name of exporter
	verbose_name = _('Export Phylogeny')
	# name of phylogeny format
	format_name = None
	# file extension of phylogeny format
	extension = None
	
	def __init__(self, taxon=None, export_to=None, *args, **kwargs):
		'''Initializes an instance of the phylogeny exporter.'''
		super(AbstractBasePhyloExporter, self).__init__(*args, **kwargs)
		self._taxon = None
		self._export_to = None
		self.taxon = taxon
		self.export_to = export_to
		
		if self.format_name is None:
			raise PhyloExporterMissingAttribute(ugettext('Exporter %s missing `format_name`.') % self)
		if self.extension is None:
			raise PhyloExporterMissingAttribute(ugettext('Exporter %s missing `extension`.') % self)
	
	def __repr__(self):
		'''Returns the unicode representation of an exporter instance.'''
		try:
			u = unicode(self)
		except (UnicodeEncodeError, UnicodeDecodeError):
			u = '[Bad Unicode data]'
		return u'<%s: %s>' % (self.__class__.__name__, u)
	
	def __unicode__(self):
		'''Returns a unicode string of an export instance's verbose name.'''
		if self.taxon:
			return u'%s' % self.taxon
		return u'%s' % self.verbose_name
	
	def __call__(self):
		'''Returns the phylogeny encoded in a string-based phylogeny format.'''
		pass
	
	@property
	def taxon(self):
		'''
		A Taxon model instance (the root for the phylogeny) associated with the
		exporter.  Raises PhyloExporterTaxonNotProvided error if no taxon
		was provied.
		'''
		return self._taxon
	
	@taxon.setter
	def taxon(self, taxon):
		'''
		Sets the value of the `taxon` property if the passed object is a Taxon
		model instance.
		'''
		if isinstance(taxon, Taxon):
			self._taxon = taxon
		elif taxon is not None:
			raise PhyloExporterUnsupportedTaxonAssignment(ugettext('Attempted to assign an object via the `taxon` property that is not a Taxon model instance.'))
		elif taxon is None:
			self._taxon = None
	
	@property
	def export_to(self):
		'''
		The path where the exporter should store the phylogeny when using
		the `save` method.
		'''
		if callable(self._export_to):
			export_to = '%s' % self._export_to()
		elif self._export_to:
			export_to = '%s' % self._export_to
		else:
			export_to = None
		
		return export_to
	
	@export_to.setter
	def export_to(self, export_to):
		'''Sets the value of the `export_to` property.'''
		self._export_to = export_to
	
	@abstractmethod
	def get_object(self):
		'''Returns an object representating the phylogeny to export.'''
		pass
	
	@abstractmethod
	def save(self):
		'''Saves the phylogeny to file, database, or other storage.'''
		pass
	

class AbstractBaseBiopythonPhyloExporter(AbstractBasePhyloExporter):
	'''Exports a phylogeny rooted on a given taxon to a Biopython phylogeny.'''
	__metaclass__ = ABCMeta
	verbose_name = _('Export Biopython Phylogeny')
	
	def __call__(self):
		'''Returns a string representation of the PhyloXML phylogeny.'''
		return self.get_object().format(self.format_name)
	
	def get_clade_for_taxon(self, taxon, parent_clade=None):
		'''
		Marshals data from taxon and its children recursively to new Clade(s).
		Returns the new root clade object.
		
		Biopython's PhyloXML library is used because it is the most
		comprehensive available and may easily be converted to other formats,
		such as Nexus and Newick.
		
		In general, Biopython clades and phylogenetic tree files cannot represent
		all data about taxa.  Use these for exporting basic phylogenetic trees to
		other applications.  Do not use these for archival purposes.
		'''
		date = None
		taxonomies = []
		distributions = []
		references = []
		
		# create date
		if taxon.appearance_date():
			date = Phylo.PhyloXML.Date(
				unit=taxon.appearance_date_unit,
				desc=taxon.appearance_date_annotation,
				minimum=taxon.appearance_date_min_value,
				maximum=taxon.appearance_date_max_value
			)
		
		# create taxonomies
		for taxonomy_record in taxon.taxonomyrecord_set.all():
			taxonomies += [Phylo.PhyloXML.Taxonomy(
				id=Phylo.PhyloXML.Id(value=taxonomy_record.record_id, provider=u'%s' % taxonomy_record.database),
				uri=Phylo.PhyloXML.Uri(value=u'%s' % (taxonomy_record.url or taxonomy_record.database.url))
			)]
		
		taxonomies = taxonomies
		
		# create distributions
		if taxon.distribution:
			distributions += [Phylo.PhyloXML.Distribution(
				desc=taxon.distribution
			)]
		
		for distribution_point in taxon.distributionpoint_set.all():
			distributions += [Phylo.PhyloXML.Distribution(
				desc=distribution_point.place_name,
				points=[Phylo.PhyloXML.Point(geodetic_datum='WGS84', lat=distribution_point.latitude, long=distribution_point.longitude)]
			)]
		
		distributions = distributions
		
		# create references (literary)
		for citation in taxon.citation_set.all():
			references += [Phylo.PhyloXML.Reference(
				desc=u'%s %s' % (citation.description, citation.url,),
				doi=citation.doi
			)]
		
		references = references
		
		# create new clade
		clade = Phylo.PhyloXML.Clade(
			branch_length=taxon.branch_length or 1.0,
			name=taxon.name,
			date=date,
			taxonomies=taxonomies,
			distributions=distributions,
			references=references
		)
		
		if parent_clade:
			parent_clade.clades += [clade]
		
		# recurse into child taxa
		for child_taxon in taxon.get_children():
			self.get_clade_for_taxon(child_taxon, parent_clade=clade)
		
		return clade
	
	def get_object(self):
		'''Returns a Biopython phylogeny object.'''
		clade = self.get_clade_for_taxon(self.taxon)
		phylogeny = clade.to_phylogeny()
		return phylogeny
	
	def save(self, export_to=None):
		'''Saves the PhyloXML phylogeny to file.'''
		if export_to is not None:
			self.export_to = export_to
		Phylo.write(self.get_object(), self.export_to, self.format_name)
	

class PhyloXMLPhyloExporter(AbstractBaseBiopythonPhyloExporter):
	'''Exports a phylogeny to a Biopython PhyloXML phylogeny.'''
	verbose_name = _('Export PhyloXML Phylogeny')
	format_name = 'phyloxml'
	extension = 'xml'
	

class NexusPhyloExporter(AbstractBaseBiopythonPhyloExporter):
	'''Exports a phylogeny to a Biopython Nexus phylogeny.'''
	verbose_name = _('Export Nexus Phylogeny')
	format_name = 'nexus'
	extension = 'nex'
	

class NewickPhyloExporter(AbstractBaseBiopythonPhyloExporter):
	'''Exports a phylogeny to a Biopython Newick phylogeny.'''
	verbose_name = _('Export Newick Phylogeny')
	format_name = 'newick'
	extension = 'tree'
	

class JSPhyloSVGPhyloXMLPhyloExporter(AbstractBasePhyloExporter):
	'''Exports a phylogeny to a jsPhyloSVG dialect of PhyloXML.'''
	verbose_name = _('Export jsPhyloSVG PhyloXML')
	format_name = 'phyloxml-jsphylosvg'
	extension = 'xml'
	
	def __call__(self):
		'''Returns a jsPhyloSVG PhyloXML string.'''
		return u'%s' % self.get_object()
	
	def get_object(self):
		'''Returns a jsPhyloSVG PhyloXML string.'''
		template_path = 'phylogeny/exporters/%s/%s.%s'
		template = get_template(template_path % (self.format_name, 'phylogeny', self.extension,))
		context = Context({
			'taxa_categories': TaxaCategory.objects.all,
			'colors_app_installed': ('colors' in settings.INSTALLED_APPS),
			'object': self.taxon,
			'clade_template_path': template_path % (self.format_name, 'clade', self.extension,)
		})
		return template.render(context)
	
	def save(self, export_to=None):
		'''Saves the jsPhyloSVG PhyloXML to file.'''
		if export_to is not None:
			self.export_to = export_to
		output = self()
		with open(self.export_to, 'w') as open_file:
			open_file.write(output)
	

# registry is used to register exporter classes and report on them
# throughout the app
exporter_registry = ExporterRegistry()
# register concrete exporter classes
exporter_registry.register(PhyloXMLPhyloExporter)
exporter_registry.register(NexusPhyloExporter)
exporter_registry.register(NewickPhyloExporter)
exporter_registry.register(JSPhyloSVGPhyloXMLPhyloExporter)
