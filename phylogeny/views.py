from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormView
from django import forms
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from phylogeny.models import Taxon
from phylogeny.forms import PhylogenyImportForm
from phylogeny.exceptions import PhylogenyImportMergeConflict
from phylogeny.utils import get_phylogeny, import_phylogeny


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


class PhylogenyAdminImportView(FormView):
	'''
	Renders a form for importing a phylogeny from a file upload.  Handles
	importing uploaded file into database.
	'''
	template_name = 'admin/phylogeny/import_form.html'
	form_class = PhylogenyImportForm
	
	def render_to_response(self, context, **kwargs):
		'''
		Renders a phylogeny import form.
		'''
		context.update({'is_popup': True})
		return super(PhylogenyAdminImportView, self).render_to_response(context)
	
	def post(self, request, *args, **kwargs):
		'''
		Processes file upload as a phylogeny import if form is valid.
		'''
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		
		if form.is_valid():
			format = form.cleaned_data.get('file_format')
			try:
				for file_field in request.FILES:
					import_phylogeny(path=request.FILES[file_field], format=format)
			except PhylogenyImportMergeConflict as exception:
				form._errors['file_field'] = form.error_class(['%s' % exception])
				return self.render_to_response({'form': form})
			except:
				form._errors['file_field'] = form.error_class([_('An error occurred during import.  Please verify the file format and file contents.  If the error persists, try importing a different file or format.')])
				return self.render_to_response({'form': form})
		
		messages.success(request, _('Successfully imported phylogeny.'))
		
		return HttpResponse('''
			<script type="text/javascript">
				opener.location=opener.location;
				window.close();
			</script>
		''')

