'''
Imports a phylogenetic tree (especially as from the command line).
'''
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from phylogeny.importers import importer_registry


class Command(BaseCommand):
	args = '<path>'
	help = _('Imports a phylogenetic tree into the database')
	option_list = BaseCommand.option_list + (
		make_option('--format', '-f', dest='format', default='phyloxml', help=_('A phylogeny file format supported by Biopython ("phyloxml", "nexus", or "newick")')),
	)
	
	def handle(self, *args, **options):
		try:
			path = args[0]
		except:
			raise CommandError(_('Phylogeny path missing. For more information type:\npython manage.py help import-phylogeny'))
		
		format_name = options['format']
		importer = importer_registry.get_by_format_name(format_name)
		importer.save(import_from=path)	
		self.stdout.write(_('Successfully imported tree from "%(path)s" in format "%(format)s"\n') % {'path': path, 'format': format_name})
	
