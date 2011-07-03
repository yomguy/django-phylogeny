from os import path
from datetime import datetime
from uuid import uuid4


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
