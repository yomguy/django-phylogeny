class PhylogenyImportMergeConflict(Exception):
	"""
	A merge conflict occurred during phylogeny import and the specified merge
	strategy could not resolve it.
	"""
	pass


class PhylogenyImportNameConflict(Exception):
	'''
	A name conflict occurred during a phylogeny name scan.  Two or more clades
	have the same name within the phylogeny.
	'''
	pass

