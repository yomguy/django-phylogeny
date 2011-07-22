from django import template

from phylogeny.exporters import exporter_registry


register = template.Library()
	

@register.filter
def xml_tagify(value):
	'''
	Replaces dashes with underscores, making string appropriate for use as an
	XML tag.
	'''
	return value.replace('-', '_')
