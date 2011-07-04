from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from mptt import admin as mptt_admin

from phylogeny.models import Taxon, Citation, TaxonomyDatabase, TaxonomyRecord, DistributionPoint, TaxonImage, TaxonImageCategory


class CitationAdmin(admin.TabularInline):
	model = Citation
	extra = 1


class TaxonomyDatabaseAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}


class TaxonomyRecordAdmin(admin.TabularInline):
	model = TaxonomyRecord
	extra = 1


class DistributionPointAdmin(admin.TabularInline):
	model = DistributionPoint
	extra = 1


class TaxonImageCategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}


class TaxonImageAdmin(admin.TabularInline):
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
			leaf_pk_list += Taxon._tree_manager.root_nodes()[0].get_leafnodes().values_list('pk', flat=True)
		
		if self.value() == 'yes':
			# filters items in that have a primary key in the list of primary
			# keys of leaf nodes
			return queryset.filter(pk__in=leaf_pk_list)
		
		if self.value() == 'no':
			# filters items out that have a primary key in the list of primary
			# keys of leaf nodes
			return queryset.filter(~Q(pk__in=leaf_pk_list))


class TaxonAdmin(mptt_admin.MPTTModelAdmin):
	list_display = ('name', 'rank', 'is_leaf_node',)
	list_filter = (LeafNodeListFilter,)
	search_fields = ('name', 'common_name', 'rank',)
	readonly_fields = ('is_leaf_node',)
	prepopulated_fields = {'slug': ('name',)}
	save_on_top = True
	fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': (('name', 'slug',), 'rank', 'is_leaf_node',)
		}),
		(_('general information'), {
			'fields': (('common_name', 'tagline',), 'description', 'ecology', 'distribution')
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
			'fields': (('color', 'body_length_value', 'body_length_unit',), ('social_unit_type', 'social_unit_size_min', 'social_unit_size_max',), 'social_unit_annotation',)
		}),
		(_('tree'), {
			'classes': ('collapse',),
			'fields': (('branch_length', 'parent',),)
		})
	)


admin.site.register(TaxonomyDatabase, TaxonomyDatabaseAdmin)
admin.site.register(TaxonImageCategory, TaxonImageCategoryAdmin)
admin.site.register(Taxon, TaxonAdmin)
