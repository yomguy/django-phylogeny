from django.db import models
from django.utils.translation import ugettext_lazy as _

from mptt import models as mptt_models
from Bio.Phylo.PhyloXML import Taxonomy

from phylogeny import app_settings


class Taxon(mptt_models.MPTTModel):
	'''
	Represents a phylogenetic taxon as a tree node.
	'''
	# identity
	name = models.CharField(_('scientific name'), max_length=256)
	slug = models.SlugField(_('slug'), unique=True, help_text=_('short label containing only letters, numbers, underscores, and/or hyphens; generally used in URLs'))
	# rank
	rank = models.CharField(_('rank'), choices=app_settings.TAXON_RANK_CHOICES, max_length=32, blank=True)
	# attribution
	author = models.CharField(_('author'), max_length=256, blank=True, help_text=_('name of author'))
	year_of_description = models.SmallIntegerField(_('year of description'), null=True, blank=True)
	# descriptive information
	common_name = models.CharField(_('common name'), max_length=256, blank=True)
	tagline = models.CharField(_('tagline'), max_length=256, blank=True, help_text=_('very short description'))
	description = models.TextField(_('general description'), blank=True)
	ecology = models.TextField(_('ecology'), blank=True)
	distribution = models.TextField(_('distribution'), blank=True, help_text=_('explanation of distribution'))
	# appearance date
	appearance_date_min_value = models.SmallIntegerField(_('minimum date of appearance value'), null=True, blank=True)
	appearance_date_max_value = models.SmallIntegerField(_('maximum date of appearance value'), null=True, blank=True)
	appearance_date_unit = models.CharField(_('appearance date unit'), default=app_settings.TAXON_APPEARANCE_DATE_UNIT_DEFAULT, choices=app_settings.TAXON_APPEARANCE_DATE_UNIT_CHOICES, max_length=3, blank=True)
	appearance_date_annotation = models.TextField(_('appearance date annotation'), blank=True)
	# color
	color = models.CharField(_('color'), max_length=64, blank=True)
	# body length
	body_length_value = models.SmallIntegerField(_('body length value'), null=True, blank=True, help_text=_('metric units'))
	body_length_unit = models.CharField(_('body length unit'), default=app_settings.TAXON_BODY_LENGTH_UNIT_DEFAULT, choices=app_settings.TAXON_BODY_LENGTH_UNIT_CHOICES, max_length=2, blank=True, help_text=_('metric unit'))
	# tree information
	branch_length = models.FloatField(_('branch length'), default=app_settings.TAXON_BRANCH_LENGTH_DEFAULT, null=True, blank=True)
	parent = mptt_models.TreeForeignKey('self', verbose_name=_('parent taxon'), null=True, blank=True, related_name='children')
	# dates
	date_created = models.DateTimeField(_('date created'), auto_now_add=True)
	date_modified = models.DateTimeField( _('date modified'), auto_now=True)
	
	class Meta:
		verbose_name = _('taxon')
		verbose_name_plural = _('taxa')
	
	def __unicode__(self):
		return u'%s' % self.name
		
	def is_leaf_node(self):
		return super(Taxon, self).is_leaf_node()
	is_leaf_node.boolean = True
	
	def body_length(self):
		'''
		Returns a string with body length value and unit if body length value
		is specified.
		'''
		if self.body_length_value:
			return u'%s%s' % (self.body_length_value, self.get_body_length_unit_display(),)
	
	def appearance_date(self):
		'''
		Returns a string with appearance date and unit if either or both is
		specified:  appearance date min value or max value.
		'''
		appearance_date = u''
		if self.appearance_date_min_value or self.appearance_date_max_value:
			appearance_date = u'%s %s' % (self.appearance_date_min_value or self.appearance_date_max_value, self.get_appearance_date_unit_display(),)
		if self.appearance_date_min_value and self.appearance_date_max_value:
			appearance_date = u'%s \u2012 %s %s' % (self.appearance_date_min_value, self.appearance_date_max_value, self.get_appearance_date_unit_display(),)
		return appearance_date


class Citation(models.Model):
	'''
	Cites source work for a taxon.
	'''
	description = models.CharField(_('description'), unique=True, max_length=256)
	url = models.URLField(_('URL'), verify_exists=False, max_length=512, blank=True)
	doi = models.CharField(_(u'DOI\u00AE: digital object identifier'), max_length=256, blank=True)
	taxon = models.ManyToManyField(Taxon, verbose_name=_('taxon'), through='TaxonCitation')
	
	class Meta:
		verbose_name = _('citation')
		verbose_name_plural = _('citations')
	
	def __unicode__(self):
		if self.doi:
			return u'%s (%s)' % (self.description, self.doi,)
		return u'%s' % self.description


class TaxonCitation(models.Model):
	'''
	Specifies a relationship between a citation and a taxon.
	'''
	taxon = models.ForeignKey(Taxon, verbose_name=_('taxon'))
	citation = models.ForeignKey(Citation, verbose_name=_('citation'))
	
	class Meta:
		verbose_name = _('taxon citation')
		verbose_name_plural = _('taxon citations')
		unique_together = ('taxon', 'citation',)
	
	def __unicode__(self):
		return u'"%s" cites:  %s' % (self.taxon, self.citation,)
