'''
Exception classes.
'''
class PhyloExporterUnsupportedTaxonAssignment(Exception):
	'''
	A taxon assignment with an object that is not a Taxon model instance
	was attempted.
	'''
	pass


class PhyloExporterMissingAttribute(Exception):
	'''
	A required attribute on the exporter class is missing.
	'''
	pass
	

class PhyloExporterRegistryOnlyClassesMayRegister(Exception):
	'''
	Exporter registry method `register` was called with a non-class argument.
	'''
	pass
	

class PhyloExporterRegistryClassAlreadyRegistered(Exception):
	'''Exporter class attempted to register more than once.'''
	pass
	

class PhyloExporterRegistryExporterNotFound(Exception):
	'''Exporter class not found.'''
	pass
	

class PhylogenyImportMergeConflict(Exception):
	'''
	A merge conflict occurred during phylogeny import and the specified merge
	strategy could not resolve it.
	'''
	pass


class PhylogenyImportNameConflict(Exception):
	'''
	A name conflict occurred during a phylogeny name scan.  Two or more clades
	have the same name within the phylogeny.
	'''
	pass


class PhyloImporterMissingAttribute(Exception):
	'''
	A required attribute on the importer class is missing.
	'''
	pass


class PhyloImporterRegistryOnlyClassesMayRegister(Exception):
	'''
	Importer registry method `register` was called with a non-class argument.
	'''
	pass


class PhyloImporterRegistryClassAlreadyRegistered(Exception):
	'''Importer class attempted to register more than once.'''
	pass


class PhyloImporterRegistryImporterNotFound(Exception):
	'''Importer class not found.'''
	pass


class PhylogenyDjangoColorsNotInstalled(Exception):
	'''Django Colors app is not installed.'''
	pass

