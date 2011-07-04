from os import path
from datetime import datetime
from uuid import uuid4

from Bio.Phylo import PhyloXML, write


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
