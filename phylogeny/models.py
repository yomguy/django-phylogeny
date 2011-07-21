from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mptt import models as mptt_models
from Bio.Phylo.PhyloXML import Taxonomy

from phylogeny import app_settings, utils, managers


ColorField = models.CharField
# try loading color picker field from the django-colors app
# http://code.google.com/p/django-colors/
# fallback on CharField if django-colors is not available
if 'colors' in settings.INSTALLED_APPS:	
	try:
		from colors.fields import ColorField
	except:
		pass


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
	# social unit
	social_unit_type = models.CharField(_('social unit type'), default=app_settings.TAXON_SOCIAL_UNIT_DEFAULT, choices=app_settings.TAXON_SOCIAL_UNIT_CHOICES, max_length=32, blank=True)
	social_unit_size_min = models.SmallIntegerField(_('minimum social unit size'), null=True, blank=True, help_text=_('number of individuals'))
	social_unit_size_max = models.SmallIntegerField(_('maximum social unit size'), null=True, blank=True, help_text=_('number of individuals'))
	social_unit_annotation = models.TextField(_('social unit annotation'), blank=True)
	# tree information
	branch_length = models.FloatField(_('branch length'), default=app_settings.TAXON_BRANCH_LENGTH_DEFAULT, null=True, blank=True)
	parent = mptt_models.TreeForeignKey('self', verbose_name=_('parent taxon'), null=True, blank=True, related_name='children')
	# dates
	date_created = models.DateTimeField(_('date created'), auto_now_add=True)
	date_modified = models.DateTimeField( _('date modified'), auto_now=True)
	
	# manager
	objects = managers.TaxonManager()
	
	class Meta:
		verbose_name = _('taxon')
		verbose_name_plural = _('taxa')
	
	def __unicode__(self):
		return u'%s' % self.name
	
	def natural_key(self):
		return (self.slug,)
	
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
	description = models.CharField(_('description'), max_length=256)
	url = models.URLField(_('URL'), verify_exists=False, max_length=512, blank=True)
	doi = models.CharField(_(u'DOI\u00AE: digital object identifier'), max_length=256, blank=True)
	taxon = models.ForeignKey(Taxon, verbose_name=_('taxon'))
	
	class Meta:
		verbose_name = _('citation')
		verbose_name_plural = _('citations')
	
	def __unicode__(self):
		if self.doi:
			return u'%s:  %s (%s)' % (self.taxon, self.description, self.doi,)
		return u'%s:  %s' % (self.taxon, self.description,)


class TaxonomyDatabase(models.Model):
	'''
	Represents an external taxonomic database.
	'''
	name = models.CharField(_('taxonomy database name'), max_length=256, help_text=_('name of an external taxonomic database such as NCBI, ITIS, etc'))
	slug = models.SlugField(_('slug'), unique=True, help_text=_('short label containing only letters, numbers, underscores, and/or hyphens; generally used in URLs'))
	url = models.URLField(_('URL'), max_length=512)
	
	# manager
	objects = managers.TaxonomyDatabaseManager()
	
	class Meta:
		verbose_name = _('taxonomy database')
		verbose_name_plural = _('taxonomy databases')
	
	def __unicode__(self):
		return u'%s' % self.name
	
	def natural_key(self):
		return (self.slug,)


class TaxonomyRecord(models.Model):
	'''
	Refers to a taxon record in an external taxonomic database
	(such as NCBI, ITIS, etc).
	'''
	taxon = models.ForeignKey(Taxon, verbose_name=_('taxon'))
	database = models.ForeignKey(TaxonomyDatabase, verbose_name=_('taxonomy database'))
	record_id = models.CharField(_('taxon record ID'), max_length=256, help_text=_('ID of this record in the specified taxonomic database'))
	url = models.URLField(_('URL'), max_length=512, blank=True, help_text=_('URL of this record in the specified taxonomic database'))
	
	# manager
	objects = managers.TaxonomyRecordManager()
	
	class Meta:
		verbose_name = _('taxonomy record')
		verbose_name_plural = _('taxonomy records')
		unique_together = ('taxon', 'database', 'record_id',)
	
	def __unicode__(self):
		return u'%s %s' % (self.database, self.record_id,)
	
	def natural_key(self):
		return (self.record_id,) + self.database.natural_key() + self.taxon.natural_key()


class DistributionPoint(models.Model):
	'''
	Marks a geographic point where a taxon appears.
	'''
	place_name = models.CharField(_('place name'), max_length=64, blank=True, help_text=_('name of a place where taxon appears; use with or instead of latitude and longitude'))
	latitude = models.FloatField(_('latitude'))
	longitude = models.FloatField(_('longitude'))
	taxon = models.ForeignKey(Taxon, verbose_name=_('taxon'))
	
	# manager
	objects = managers.DistributionPointManager()
	
	class Meta:
		verbose_name = _('distribution point')
		verbose_name_plural = _('distribution points')
		unique_together = ('latitude', 'longitude', 'taxon',)
	
	def __unicode__(self):
		string = u'%s' % self.place_name
		if self.latitude and self.longitude:
			string = u'(%+f, %+f)' % (self.latitude, self.longitude,)
		if self.place_name and self.latitude and self.longitude:
			string = u'%s (%+f, %+f)' % (self.place_name, self.latitude, self.longitude,)
		return string
	
	def natural_key(self):
		return (self.latitude, self.longitude,) + self.taxon.natural_key()


class TaxonImageCategory(models.Model):
	'''
	Describes a category of image.
	'''
	name = models.CharField(_('category name'), max_length=256)
	slug = models.SlugField(_('slug'), unique=True, help_text=_('short label containing only letters, numbers, underscores, and/or hyphens; generally used in URLs'))
	
	class Meta:
		verbose_name = _('taxon image category')
		verbose_name_plural = _('taxon image categories')
	
	def __unicode__(self):
		return u'%s' % self.name


class TaxonImage(models.Model):
	'''
	Stores an image for a taxon.
	'''
	caption = models.CharField(_('caption'), max_length=256)
	credit = models.CharField(_('credit'), max_length=128, blank=True)
	category = models.ForeignKey(TaxonImageCategory, verbose_name=_('category'), null=True, blank=True)
	primary = models.BooleanField(_('primary image'), help_text=_('primary image for specified taxon'))
	image = models.ImageField(_('source'), upload_to=utils.get_taxon_image_upload_to)
	width = models.IntegerField(_('width'), null=True, blank=True, help_text=_('width in pixels of this image'))
	height = models.IntegerField(_('height'), null=True, blank=True, help_text=_('height in pixels of this image'))
	taxon = models.ForeignKey(Taxon, verbose_name=_('taxon'))
	
	class Meta:
		verbose_name = _('taxon image')
		verbose_name_plural = _('taxon images')
	
	def __unicode__(self):
		return u'%s' % self.caption


class Color(models.Model):
	'''
	Represents a reusable color style.  Color styles are primarily used by the
	jsPhyloSVG PhyloXML exporter and the jsPhyloSVG phylogeny tree visualizer.
	'''
	name = models.CharField(_('name'), max_length=64)
	slug = models.SlugField(_('slug'), unique=True, help_text=_('short label containing only letters, numbers, underscores, and/or hyphens; generally used in URLs'))
	color = ColorField(_('color'), max_length=7)
	
	# manager
	objects = managers.ColorManager()
	
	class Meta:
		verbose_name = _('color')
		verbose_name_plural = _('colors')
	
	def __unicode__(self):
		return u'%s' % self.name
	
	def natural_key(self):
		return (self.slug,)


class TaxonBackgroundColor(models.Model):
	'''
	Associates a background color with a taxon.
	'''
	color = models.ForeignKey(Color, verbose_name=_('color'))
	taxon = models.ForeignKey(Taxon, verbose_name=_('taxon'))
	
	# manager
	objects = managers.TaxonBackgroundColorManager()
	
	class Meta:
		verbose_name = _('taxon background color')
		verbose_name_plural = _('taxa background colors')
		unique_together = ('color', 'taxon',)
	
	def __unicode__(self):
		return u'%s: %s' % (self.color, self.taxon,)
	
	def natural_key(self):
		return self.color.natural_key() + self.taxon.natural_key()

