from os import path
from datetime import datetime
from uuid import uuid4

from django.db import transaction
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from Bio.Phylo import PhyloXML, write, parse

from phylogeny.exceptions import PhylogenyImportMergeConflict, PhylogenyImportNameConflict


def get_taxon_image_upload_to(instance, filename):
	'''
	Generates an ``upload_to`` path based on the model name and the current date.

	Upload paths are in the format:
		phylogeny/{{ model_name }}/{{ year }}/{{ month }}/
	'''
	media_ext = ''
	media_filename, media_ext = path.splitext(filename)
	return '%s/%s/%s/%s-%s-%s-%s%s' % (
		instance.__class__._meta.app_label,
		instance.taxon.__class__._meta.module_name,
		instance.taxon.slug,
		datetime.now().year,
		datetime.now().month,
		datetime.now().day,
		datetime.now().microsecond,
		media_ext.lower()
	)


def slugify_unique(value, model, slugfield='slug'):
	'''
	Returns a slug on a name which is unique within a model's table.
	'''
	suffix = 0
	potential = base = slugify(value)
	while True:
		if suffix:
			potential = "-".join([base, str(suffix)])
		if not model.objects.filter(**{slugfield: potential}).count():
			return potential
		# we hit a conflicting slug, so bump the suffix & try again
		suffix += 1


def get_taxon_name_from_clade(clade):
	'''
	Generates a name suitable for use by a taxon from the given clade.
	'''
	# base name
	taxon_name = clade.name or 'none'
	# sometimes the name can be in a taxonomy, but not the clade itself
	if hasattr(clade, 'taxonomies') and len(clade.taxonomies) > 0 and hasattr(clade.taxonomies[0], 'scientific_name'):
		taxon_name = clade.taxonomies[0].scientific_name or taxon_name
	return taxon_name


def get_taxon_for_clade(clade, parent_taxon=None):
	'''
	Imports data from a phylogeny and saves taxa to the database.
	
	Merge conflicts can arise when an imported clade's name matches an existing
	taxon's name.  In the case of conflicts, a merge strategy is used.  The
	default merge strategy is to abort import, leaving existing taxa alone and
	rolling back all partially-imported taxa.
	
	Available merge strategies are:
		
		None:  the default merge strategy is to abort import, leaving existing
			taxa alone and rolling back all partially-imported taxa.
	'''
	from phylogeny.models import Taxon, Citation, TaxonomyDatabase, TaxonomyRecord, DistributionPoint
	
	# merge strategy None is the only supported strategy at this time
	merge_strategy = None
	
	taxon_name = get_taxon_name_from_clade(clade)
	
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
		raise PhylogenyImportMergeConflict(_('Merge conflict occurred:  name "%(taxon_name)s" already exists.  Import aborted.  This may be caused by two clades having the same name in the phylogeny file or by a clade having the same name as an existing taxon.  Please change the name of the existing taxon or change the name of the taxon in the import file.') % {'taxon_name': taxon.name})
	
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
		get_taxon_for_clade(child_clade, parent_taxon=taxon)
	
	return taxon
	

@transaction.commit_on_success
def import_phylogeny(path=None, format='phyloxml'):
	'''
	Imports phylogenetic tree(s) from `path` in the specified format
	(`phyloxml`, `nexus`, `newick`) default `phyloxml`.
	'''
	trees = parse(path, format)
	for tree in trees:
		get_taxon_for_clade(tree.root)
	

