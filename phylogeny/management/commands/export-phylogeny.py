from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from phylogeny.models import Taxon
from phylogeny.utils import export_phylogeny


class Command(BaseCommand):
	args = '<taxon_slug> <path>'
	help = _('Exports a phylogenetic tree rooted on <taxon_slug> to the specified file in the specified format (default format is phyloxml)')
	option_list = BaseCommand.option_list + (
		make_option(
			'--format',
			'-f',
			dest='format',
			default='phyloxml',
			help=_('A file format supported by Biopython for the exported phylogenetic tree ("phyloxml", "nexus", or "newick")')
		),
	)
	
	def handle(self, *args, **options):
		try:
			taxon_slug = args[0]
		except:
			raise CommandError(_('Taxon slug missing.'))
		
		try:
			taxon = Taxon.objects.get_by_natural_key(taxon_slug)
		except Taxon.DoesNotExist:
			raise CommandError(_('Taxon "%s" does not exist') % taxon_slug)
		
		try:
			path = args[1]
		except:
			raise CommandError(_('File path missing'))
		
		try:
			export_phylogeny(taxon, path=path, format=options['format'])
			self.stdout.write(_('Successfully exported tree rooted on taxon "%s" to "%s" in format "%s"\n') % (taxon_slug, path, options['format'],))
		except:
			raise CommandError(_('Failed exporting phylogeny to "%s" in format "%s"') % (path, options['format'],))
