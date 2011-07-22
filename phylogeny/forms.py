'''
Forms by Django Phylogeny.
'''
from django import forms
from django.utils.translation import ugettext_lazy as _

from phylogeny import app_settings


class PhylogenyImportForm(forms.Form):
	file_field = forms.FileField(label=_('phylogeny file'))
	file_format = forms.ChoiceField(label=_('format'), choices=app_settings.PHYLOGENY_IMPORT_FILE_FORMAT_CHOICES)
	
