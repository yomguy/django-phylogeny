'''
General template tags for the Django Phylogeny app.
'''
from django import template
from django.template.defaultfilters import stringfilter

from phylogeny.exporters import exporter_registry


register = template.Library()
	

@register.filter
@stringfilter
def xml_tagify(value):
	'''
	Replaces dashes with underscores, making string appropriate for use as an
	XML tag.
	'''
	return value.replace('-', '_')
