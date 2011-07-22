from modeltranslation.translator import translator, TranslationOptions

from phylogeny.models import Taxon, Citation, DistributionPoint, TaxonImageCategory, TaxonImage, TaxaCategory


class TaxonTranslationOptions(TranslationOptions):
	fields = ('common_name', 'tagline', 'description', 'ecology', 'distribution', 'appearance_date_annotation', 'color', 'social_unit_annotation',)


class CitationTranslationOptions(TranslationOptions):
	fields = ('description',)


class DistributionPointTranslationOptions(TranslationOptions):
	fields = ('place_name',)


class TaxonImageCategoryTranslationOptions(TranslationOptions):
	fields = ('name',)


class TaxonImageTranslationOptions(TranslationOptions):
	fields = ('caption', 'credit',)


class TaxaCategoryTranslationOptions(TranslationOptions):
	fields = ('name', 'description',)


translator.register(Taxon, TaxonTranslationOptions)
translator.register(Citation, CitationTranslationOptions)
translator.register(DistributionPoint, DistributionPointTranslationOptions)
translator.register(TaxonImageCategory, TaxonImageCategoryTranslationOptions)
translator.register(TaxonImage, TaxonImageTranslationOptions)
translator.register(TaxaCategory, TaxaCategoryTranslationOptions)
