from django import template
from django.utils.translation import ugettext

from phylogeny.exporters import exporter_registry


register = template.Library()


class ExportersNode(template.Node):
	def __init__(self, var_name):
		self.var_name = var_name
	
	def render(self, context):
		context[self.var_name] = exporter_registry.get_exporters
		return ''
	

@register.tag
def get_exporters(parser, token):
	'''
	Adds a tuple of registered exporter classes to the context as `var_name`.
	
	Usage::
		
		{% get_exporters as [var_name] %}
	'''
	bits = token.split_contents()
	if len(bits) < 3:
		raise template.TemplateSyntaxError(ugettext('%r tag has invalid arguments') % bits[0])
	
	var_name = bits[2]
	
	return ExportersNode(var_name)

