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
TAXON_IMAGE_KIND_CHOICES = (
	('photo', _('photograph'),),
	('illustration', _('illustration'),),
)


# default field values
TAXON_BRANCH_LENGTH_DEFAULT = 1.0
TAXON_BODY_LENGTH_UNIT_DEFAULT = 'mm'
TAXON_APPEARANCE_DATE_UNIT_DEFAULT = 'mya'
TAXON_SOCIAL_UNIT_DEFAULT = ''
TAXON_IMAGE_KIND_DEFAULT = ''
