from django.conf.urls.defaults import patterns, url, include
from django.utils.translation import ugettext_lazy as _

from phylogeny.views import PhylogenyExportView


base_urlpatterns = patterns('',
	url(_(r'^export/(?P<slug>[-\w]+)\.(?P<ext>(xml|nex|tree))$'), PhylogenyExportView.as_view(), name='export'),
)

# include base url patterns into the `phylogeny` namespace
urlpatterns = patterns('',
	url(r'^', include(base_urlpatterns, namespace='phylogeny')),
)
