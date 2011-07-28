'''
Django view classes for the Phylogeny app.
'''
from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from phylogeny.models import Taxon
from phylogeny.forms import PhylogenyImportForm
from phylogeny.exporters import exporter_registry
from phylogeny.exceptions import PhylogenyImportMergeConflict
from phylogeny.importers import importer_registry


class PhylogenyExportView(BaseDetailView):
	'''
	Exports a phylogeny to a downloadable file.  The phylogeny is rooted on the
	given taxon and in the format specified by the `ext` argument.  Since
	multiple exporters may share an extension, a clarifying URL parameter
	`format` may be specified with the exporter format name.
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
		format_name = self.request.GET.get('format', '')
		rank_filter = self.request.GET.get('rank_filter', '')
		
		content_type = 'text/plain'
		if ext == 'xml':
			content_type = 'application/xml'
		
		if format_name:
			exporter = exporter_registry.get_by_format_and_extension(format_name, ext)
		else:
			exporter = exporter_registry.get_by_extension(ext)
		
		exporter.taxon = self.object
		if rank_filter:
			print rank_filter
			exporter.pruning_filter = {'rank': rank_filter}
			print exporter.pruning_filter
		content = exporter()
		print kwargs
		response = HttpResponse(content, content_type=content_type, **kwargs)
		response['Content-Disposition'] = 'attachment; filename=%s.%s' % (slug, ext)
		
		return response


class PhylogenyAdminVisualizeView(DetailView):
	'''
	Renders a visualization of a phylogeny rooted on the given taxon.
	'''
	template_name = 'admin/phylogeny/visualize.html'
	queryset = Taxon.objects.all()

	def render_to_response(self, context, *args, **kwargs):
		'''
		Renders a phylogeny visualization.
		'''
		rank_filter = self.request.GET.get('rank_filter', '')
		context.update({'is_popup': True, 'rank_filter': rank_filter})
		return super(PhylogenyAdminVisualizeView, self).render_to_response(context, *args, **kwargs)


class PhylogenyAdminImportView(FormView):
	'''
	Renders a form for importing a phylogeny from a file upload.  Handles
	importing uploaded file into database.
	'''
	template_name = 'admin/phylogeny/import_form.html'
	form_class = PhylogenyImportForm
	
	def render_to_response(self, context, *args, **kwargs):
		'''
		Renders a phylogeny import form.
		'''
		context.update({'is_popup': True})
		return super(PhylogenyAdminImportView, self).render_to_response(context, *args, **kwargs)
	
	def post(self, request, *args, **kwargs):
		'''
		Processes file upload as a phylogeny import if form is valid.
		'''
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		
		if form.is_valid():
			file_format = form.cleaned_data.get('file_format')
			try:
				importer = importer_registry.get_by_format_name(file_format)
				for file_field in request.FILES:
					importer.save(import_from=request.FILES[file_field])
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

