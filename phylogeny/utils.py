'''
General purpose functions.
'''
from os import path
from datetime import datetime

from django.template.defaultfilters import slugify


def get_taxon_image_upload_to(instance, filename):
	'''
	Generates an ``upload_to`` path based on the model name and the current date.

	Upload paths are in the format:
		phylogeny/{{ model_name }}/{{ year }}/{{ month }}/
	'''
	media_ext = ''
	media_ext = path.splitext(filename)[1]
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
