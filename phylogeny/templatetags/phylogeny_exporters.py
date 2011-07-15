import re

from django import template
from django.utils.translation import ugettext

from phylogeny.exporters import exporter_registry


register = template.Library()


class ExporterNode(template.Node):
	def __init__(self, var_name):
		self.var_name = var_name
	
	def render(self, context):
		exporters = exporter_registry.exporters
		context[self.var_name] = exporters
		return ''
	

@register.tag
def get_exporters(parser, token):
	'''
	Gets a tuple of registered exporters and adds to the context as `var_name`.
	
	Usage::
		
		{% get_exporters as [var_name] %}
	'''
	bits = token.split_contents()
	if len(bits) < 3:
		raise template.TemplateSyntaxError(ugettext('%r tag has invalid arguments') % bits[0])
	
	var_name = bits[2]
	
	return ExporterNode(var_name)
	
