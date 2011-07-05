from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from phylogeny.exceptions import PhylogenyImportMergeConflict
from phylogeny.utils import import_phylogeny


class Command(BaseCommand):
	args = '<path>'
	help = _('Imports a phylogenetic tree into the database')
	option_list = BaseCommand.option_list + (
		make_option(
			'--format',
			'-f',
			dest='format',
			default='phyloxml',
			help=_('A file format supported by Biopython for the exported phylogenetic tree ("phyloxml", "nexus", or "newick")')
		),
		make_option(
			'--strategy',
			'-s',
			dest='strategy',
			default=None,
			help=_('''Merge conflicts can arise when an imported clade\'s name matches an existing taxon\'s name.  In the case of conflicts, a merge strategy is used.  The default merge strategy is to abort import, leaving existing taxa alone and rolling back all partially-imported taxa.
				
				Available merge strategies are:

					"update":  move existing taxa into the new tree structure, leaving their field data unaffected.  This strategy is useful if you just need to update a phylogeny's tree structure. The existing children of moved taxa will be unlinked, which can leave orphaned root nodes in the database.  It may be necessary to perform manual cleanup of the orphaned taxa.

					"create":  creates brand new taxa leaving existing taxa alone.
				''')
		),
	)
	
	def handle(self, *args, **options):
		try:
			path = args[0]
		except:
			raise CommandError(_('Phylogeny path missing. For more information type:\npython manage.py help import-phylogeny'))
		
		try:
			import_phylogeny(path=path, format=options['format'], merge_strategy=options['strategy'])
			self.stdout.write(_('Successfully imported tree from "%s" in format "%s" with merge strategy "%s"\n') % (path, options['format'], options['strategy']))
		except PhylogenyImportMergeConflict as exception:
			raise CommandError(u'%s' % exception)

