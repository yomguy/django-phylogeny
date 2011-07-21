from django import template
from django.utils.translation import ugettext
from django.conf import settings

from phylogeny.exceptions import PhylogenyDjangoColorsNotInstalled


if not 'colors' in settings.INSTALLED_APPS:
	raise PhylogenyDjangoColorsNotInstalled(ugettext('Django Colors app is not installed but is required by the %s tag library.	 Install Django Colors and add "colors" to INSTALLED_APPS in settings.py.') % __file__)


from colors.templatetags.colors import lightness as colors_lightness, saturation as colors_saturation, hue as colors_hue, expand_hex, hex_to_hsv


register = template.Library()


@register.filter
def lightness(x, value):
	'''
	Extends colors app lightness filter with relative changes using "+" and "-".
	
	Example usage:
	
		{{ color|lightness:"+5" }}
		{{ color|lightness:"-5" }}
		{{ color|lightness:"50" }}
	'''
	x = expand_hex(x)
	h, s, v = hex_to_hsv(x, False) if len(x) == 6 else x
	
	if str(value).startswith('+'):
		value = int(v) + int(value[1:])
		if value > 100:
			value = 100
	if str(value).startswith('-'):
		value = int(v) - int(value[1:])
		if value < 0:
			value = 0
	
	return colors_lightness(x, value)

@register.filter
def saturation(x, value):
	'''
	Extends colors app saturation filter with relative changes using "+"
	and "-".
	
	Example usage:
	
		{{ color|saturation:"+5" }}
		{{ color|saturation:"-5" }}
		{{ color|saturation:"50" }}
	'''
	x = expand_hex(x)
	h, s, v = hex_to_hsv(x, False) if len(x) == 6 else x
	
	# technically, saturation cannot increase _relatively_ from 0
	# i.e. gray remains gray regardless of saturation increase
	if s > 0:
		if str(value).startswith('+'):
			value = int(s) + int(value[1:])
			if value > 100:
				value = 100
		if str(value).startswith('-'):
			value = int(s) - int(value[1:])
			if value < 0:
				value = 0
	else:
		value = 0
	
	return colors_saturation(x, value)

@register.filter
def hue(x, value):
	'''
	Extends colors app hue filter with relative changes using "+" and "-".
	
	Example usage:
	
		{{ color|hue:"+180" }}
		{{ color|hue:"-180" }}
		{{ color|hue:"180" }}
	'''
	x = expand_hex(x)
	h, s, v = hex_to_hsv(x, False) if len(x) == 6 else x
	
	if str(value).startswith('+'):
		value = int(h) + int(value[1:])
	if str(value).startswith('-'):
		value = int(h) - int(value[1:])
	
	# compensate for values falling outside the range 0-360
	if int(value) > 360 or int(value) < 0:
		value = int(value) % 360
	
	return colors_hue(x, value)
