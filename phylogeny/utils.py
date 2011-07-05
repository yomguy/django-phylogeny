from os import path
from datetime import datetime
from uuid import uuid4

from django.db import transaction
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from Bio.Phylo import PhyloXML, write, parse

from phylogeny.exceptions import PhylogenyImportMergeConflict


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


@transaction.commit_on_success
def get_taxon_for_clade(clade, parent_taxon=None, merge_strategy=None):
	'''
	Imports data from a phylogeny and saves taxa to the database.
	
	Merge conflicts can arise when an imported clade's name matches an existing
	taxon's name.  In the case of conflicts, a merge strategy is used.  The
	default merge strategy is to abort import, leaving existing taxa alone and
	rolling back all partially-imported taxa.
	
	Available merge strategies are:
	
		"update":  move existing taxa into the new tree structure, leaving their
			field data unaffected.  This strategy is useful if you just need to
			update a phylogeny's tree structure.
			
			The existing children of moved taxa will be unlinked, which can
			leave orphaned root nodes in the database.  It may be necessary to
			perform manual cleanup of the orphaned taxa.
		
		"create":  creates brand new taxa leaving existing taxa alone.
		
		None:  the default merge strategy is to abort import, leaving existing
			taxa alone and rolling back all partially-imported taxa.
	'''
	from phylogeny.models import Taxon, TaxonomyDatabase, TaxonomyRecord, DistributionPoint
	
	# establish baseline default values for new taxon
	defaults = {
		'name': clade.name,
		'slug': slugify_unique(clade.name, Taxon),
	}
	
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
	
	# get or create a taxon matching root_clade.name
	taxon, created = Taxon.objects.get_or_create(slug=slugify(clade.name or ''), defaults=defaults)
	
	# None merge strategy
	if merge_strategy is None and not created:
		# merge strategy is None or other:
		raise PhylogenyImportMergeConflict(_('Merge conflict occurred using merge strategy None:  taxon with slug "%(taxon_slug)s" already exists.  Import aborted.') % {'taxon_slug': taxon.slug})
	
	# "update" merge strategy
	if merge_strategy == 'update' and not created:
		# unlink taxon's children (in effect orphaning them)
		for child in taxon.get_children():
			child.move_to(None)
	
	# "create" merge strategy
	if merge_strategy == 'create' and not created:
		# create a new taxon
		taxon = Taxon.objects.create(**defaults)
	
	if merge_strategy == 'create':
		# import taxonomies, distributions, and references
		for taxonomy in clade.taxonomies:
			if taxonomy.id and taxonomy.id.value and taxonomy.id.provider:
				taxonomy_database_slug = slugify_unique(taxonomy.id.provider, TaxonomyDatabase)
				taxonomy_database, c = TaxonomyDatabase.objects.get_or_create(name=taxonomy.id.provider, slug=taxonomy_database_slug)
				taxonomy_record, c = TaxonomyRecord.objects.get_or_create(taxon=taxon, database=taxonomy_database, record_id=taxonomy.id.value, url=taxonomy.uri)
		for distribution in clade.distributions:
			distribution_point, c = DistributionPoint.objects.create(taxon=taxon, place_name=distribution.desc)
			for point in distribution.points:
				distribution_point, c = DistributionPoint.objects.create(taxon=taxon, place_name=distribution.desc, latitude=point.lat, longitude=point.long)
		for reference in clade.references:
			citation, c = Citation.objects.create(taxon=taxon, description=reference.desc, doi=reference.doi)
	
	# move taxon to parent (or root if no parent)
	taxon.move_to(parent_taxon)
	
	for child_clade in clade.clades:
		get_taxon_for_clade(child_clade, parent_taxon=taxon, merge_strategy=merge_strategy)
	
	return taxon


def get_clade_for_taxon(taxon, parent_clade=None):
	'''
	Marshals data from taxon and its children recursively to new Clade(s).
	Returns the new root clade object.
	
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
		date = PhyloXML.Date(
			unit=taxon.appearance_date_unit,
			desc=taxon.appearance_date_annotation,
			minimum=taxon.appearance_date_min_value,
			maximum=taxon.appearance_date_max_value
		)
	
	# create taxonomies
	for taxonomy_record in taxon.taxonomyrecord_set.all():
		taxonomies += [PhyloXML.Taxonomy(
			id=PhyloXML.Id(value=taxonomy_record.record_id, provider=u'%s' % taxonomy_record.database),
			uri=PhyloXML.Uri(value=u'%s' % (taxonomy_record.url or taxonomy_record.database.url))
		)]
	
	taxonomies = taxonomies
	
	# create distributions
	if taxon.distribution:
		distributions += [PhyloXML.Distribution(
			desc=taxon.distribution
		)]
	
	for distribution_point in taxon.distributionpoint_set.all():
		distributions += [PhyloXML.Distribution(
			desc=distribution_point.place_name,
			points=[PhyloXML.Point(geodetic_datum='WGS84', lat=distribution_point.latitude, long=distribution_point.longitude)]
		)]
	
	distributions = distributions
	
	# create references (literary)
	for citation in taxon.citation_set.all():
		references += [PhyloXML.Reference(
			desc=u'%s %s' % (citation.description, citation.url,),
			doi=citation.doi
		)]
	
	references = references
	
	# create new clade
	clade = PhyloXML.Clade(
		branch_length=taxon.branch_length,
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
		get_clade_for_taxon(child_taxon, parent_clade=clade)
	
	return clade


def get_phylogeny(root_taxon):
	'''
	Returns a new Phylogeny of clades from a Taxon instance.
	'''
	clade = get_clade_for_taxon(root_taxon)
	phylogeny = clade.to_phylogeny()
	return phylogeny


def export_phylogeny(root_taxon, path=None, format='phyloxml'):
	'''
	Exports a phylogenetic tree rooted on `root_taxon` to the specified format
	(`phyloxml`, `nexus`, `newick`) default `phyloxml` to the file specified in
	`path`.
	'''
	phylogeny = get_phylogeny(root_taxon)
	write(phylogeny, path, format)


def import_phylogeny(path=None, format='phyloxml', merge_strategy=None):
	'''
	Imports phylogenetic tree(s) from `path` in the specified format
	(`phyloxml`, `nexus`, `newick`) default `phyloxml`.  Merge conflicts are
	resolved using the merge strategy specified by `merge_strategy`.  See
	`get_taxon_for_clade` for more information about merge strategies.
	'''
	trees = parse(path, format)
	for tree in trees:
		get_taxon_for_clade(tree.root, merge_strategy=merge_strategy)

