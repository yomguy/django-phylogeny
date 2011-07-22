'''
Exporter-related template tags.
'''
from django import template

from phylogeny.exporters import exporter_registry


register = template.Library()


@register.assignment_tag
def get_exporters():
	'''
	Adds a tuple of registered exporter classes to the context as `var_name`.
	
	Usage::
		
		{% get_exporters as [var_name] %}
	'''
	return exporter_registry.get_exporters

