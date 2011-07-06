from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView

from phylogeny.models import Taxon
from phylogeny.utils import get_phylogeny


class PhylogenyExportView(BaseDetailView):
	'''
	Exports a phylogeny to a downloadable file.  The phylogeny is rooted on the
	given taxon and in the format specified by the `ext` argument.  
	'''
	queryset = Taxon.objects.all()
	
	def render_to_response(self, context, **kwargs):
		'''
		Returns a HTTP response of the given taxon converted to a phylogenetic
		tree file format.  The user is prompted to save the file to disk (due
		to the content disposition of "attachment").
		'''
		slug = self.kwargs['slug']
		ext = self.kwargs['ext']
		
		content_type = 'text/plain'
		
		if ext == 'nex':
			format = 'nexus'
		elif ext == 'tree':
			format = 'newick'
		else:
			format = 'phyloxml'
			content_type = 'application/xml'
		
		content = get_phylogeny(self.object, flatten_to_format=format)
		
		response = HttpResponse(content, content_type=content_type, **kwargs)
		response['Content-Disposition'] = 'attachment; filename=%s.%s' % (slug, ext)
		
		return response
