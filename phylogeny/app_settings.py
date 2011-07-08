from django.utils.translation import ugettext_lazy as _

from Bio.Phylo.PhyloXML import Taxonomy


# field choices choices
TAXON_RANK_CHOICES = tuple([(rank, _(rank),) for rank in Taxonomy.ok_rank])
TAXON_BODY_LENGTH_UNIT_CHOICES = (
	(u'\u03BCm', _(u'\u03BCm'),),
	('mm', _('mm'),),
	('cm', _('cm'),),
	('m', _('m'),),
)
TAXON_APPEARANCE_DATE_UNIT_CHOICES = (
	('bya', _('billion years ago'),),
	('mya', _('million years ago'),),
	('tya', _('thousand years ago'),),
	('hya', _('hundred years ago'),),
	('ya', _('years ago'),),
)
TAXON_SOCIAL_UNIT_CHOICES = (
	('', _('none'),),
	('colony', _('colony'),),
)
PHYLOGENY_IMPORT_FILE_FORMAT_CHOICES = (
	('phyloxml', _('PhyloXML'),),
	('nexus', _('Nexus'),),
	('newick', _('Newick'),),
)


# default field values
TAXON_BRANCH_LENGTH_DEFAULT = 1.0
TAXON_BODY_LENGTH_UNIT_DEFAULT = 'mm'
TAXON_APPEARANCE_DATE_UNIT_DEFAULT = 'mya'
TAXON_SOCIAL_UNIT_DEFAULT = ''
PHYLOGENY_IMPORT_FILE_FORMAT_DEFAULT_CHOICE = PHYLOGENY_IMPORT_FILE_FORMAT_CHOICES[0][0]
