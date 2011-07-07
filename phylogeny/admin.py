from functools import update_wrapper

from django.contrib import admin
from django.db.models import Q
from django.conf.urls.defaults import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mptt import admin as mptt_admin

from phylogeny.models import Taxon, Citation, TaxonomyDatabase, TaxonomyRecord, DistributionPoint, TaxonImageCategory, TaxonImage
from phylogeny.views import PhylogenyAdminImportView


ModelAdmin = admin.ModelAdmin
TabularInline = admin.TabularInline
StackedInline = admin.StackedInline
# load modeltranslation admin classes if available
# if not present, default admin classes are used
if 'modeltranslation' in settings.INSTALLED_APPS:
	try:
		from modeltranslation import admin as modeltranslation_admin
		ModelAdmin = modeltranslation_admin.TranslationAdmin
		TabularInline = modeltranslation_admin.TranslationTabularInline
		StackedInline = modeltranslation_admin.TranslationStackedInline
	except:
		pass


class CitationAdmin(StackedInline):
	model = Citation
	extra = 1


class TaxonomyDatabaseAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}


class TaxonomyRecordAdmin(admin.TabularInline):
	model = TaxonomyRecord
	extra = 1


class DistributionPointAdmin(TabularInline):
	model = DistributionPoint
	extra = 1


class TaxonImageCategoryAdmin(ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}


class TaxonImageAdmin(StackedInline):
	model = TaxonImage
	exclude = ('width', 'height',)
	extra = 1


class LeafNodeListFilter(admin.SimpleListFilter):
	'''
	Returns a queryset of either all leaf-nodes or all non-leaf-nodes.
	
	Note that mptt could be improved by moving instance-specific query methods
	into the manager.  One would expect get_leafnodes() to be a manager method,
	but it is not (as of mptt v0.5.pre).
	'''
	title = _('leaf node')
	parameter_name = 'leaf_node'

	def lookups(self, request, model_admin):
		return (
			('yes', _('yes')),
			('no', _('no')),
		)

	def queryset(self, request, queryset):
		leaf_pk_list = []
		
		# generates a list of primary keys of all leaf nodes
		for root_node in Taxon._tree_manager.root_nodes():
			if root_node.is_leaf_node():
				leaf_pk_list += [root_node.pk]
			leaf_pk_list += root_node.get_leafnodes().values_list('pk', flat=True)
		
		if self.value() == 'yes':
			# filters items in that have a primary key in the list of primary
			# keys of leaf nodes
			return queryset.filter(pk__in=leaf_pk_list)
		
		if self.value() == 'no':
			# filters items out that have a primary key in the list of primary
			# keys of leaf nodes
			return queryset.filter(~Q(pk__in=leaf_pk_list))


class TaxonAdmin(mptt_admin.MPTTModelAdmin, ModelAdmin):
	list_display = ('name', 'rank', 'is_leaf_node',)
	list_filter = (LeafNodeListFilter,)
	search_fields = ('name', 'common_name', 'rank',)
	readonly_fields = ('is_leaf_node',)
	prepopulated_fields = {'slug': ('name',)}
	save_on_top = True
	inlines = (CitationAdmin, TaxonImageAdmin, DistributionPointAdmin, TaxonomyRecordAdmin,)
	change_list_template = ''
	fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': (('name', 'slug',), 'rank', 'is_leaf_node',)
		}),
		(_('general information'), {
			'fields': ('common_name', 'tagline', 'description', 'ecology', 'distribution',)
		}),
		(_('attribution'), {
			'classes': ('collapse', 'wide',),
			'fields': (('author', 'year_of_description',),)
		}),
		(_('appearance date'), {
			'classes': ('collapse', 'wide',),
			'fields': (('appearance_date_min_value', 'appearance_date_max_value', 'appearance_date_unit'), 'appearance_date_annotation',)
		}),
		(_('additional information'), {
			'classes': ('collapse',),
			'fields': ('color', ('body_length_value', 'body_length_unit',), ('social_unit_type', 'social_unit_size_min', 'social_unit_size_max',), 'social_unit_annotation',)
		}),
		(_('tree'), {
			'classes': ('collapse',),
			'fields': (('branch_length', 'parent',),)
		})
	)
	
	def get_urls(self):
		'''
		Adds custom admin URLs for taxon management.
		'''
		def wrap(view):
			def wrapper(*args, **kwargs):
				return self.admin_site.admin_view(view)(*args, **kwargs)
			return update_wrapper(wrapper, view)
			
		urls = super(TaxonAdmin, self).get_urls()
		
		base_taxon_admin_urls = patterns('',
			url(_(r'^import/$'), wrap(PhylogenyAdminImportView.as_view()), name='import'),
		)
		
		taxon_admin_urls = patterns('',
			url(r'^', include(base_taxon_admin_urls, namespace='phylogeny')),
		)
		
		return taxon_admin_urls + urls


admin.site.register(TaxonomyDatabase, TaxonomyDatabaseAdmin)
admin.site.register(TaxonImageCategory, TaxonImageCategoryAdmin)
admin.site.register(Taxon, TaxonAdmin)
