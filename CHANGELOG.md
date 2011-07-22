# Django Phylogeny Changelog


## v0.5.2 (2011.july.22):

* General codebase cleanup:  many suggestions from the pylint tool implemented.
* Added more docstrings throughout app.
* Added @stringfilter decorator on string output filters.
* Simplified get_exporteres template tag with @register.assignment_tag decorator.
* Removed unused init file in fixtures/ folder.


## v0.5.1 (2011.july.22):

* Replaced color/taxon background color models with taxon category model throughout app.


## v0.5 (2011.july.21):

* Added exporter for jsPhyloSVG dialect of PhyloXML.
* Added tests for js phylosvg phyloxml exporter.
* Added color and taxonbackgroundcolor models to associate taxa with background colors; updated jsphylosvg phyloxml exporter to support background colors.
* Added support for optional URL parameter on phylogeny export view `format` which clarifies the exporter to use by format name.
* Added initial support for exporting clade colors via phyloxml-jsphylosvg exporter.
* Improved gradient generation in jsphylosvg phyloxml exporter with color filters (filters based on those found in the Django Colors app): lightness, saturation, and hue filters may accept relative arguments when argument is preceeded with "+" or "-".
* Improved admin popup window size for phylogeny visualization.


## v0.4.1 (2011.july.18):

* Added tests for class-based importers.
* Added tests for import registry.


## v0.4 (2011.july.18):

* Added class-based importers (importers.py).
* Added "importer registry" to manage importer classes.  Importer registry makes it easier to add and remove importers to the app with very little effort.  Importer registry provides an interface to register available importers and to subsequently get them, allowing code relying on importers to be generic.
* Added support throughout app for class-based importers via the importer registry including:  view class PhylogenyAdminImportView and import management command import-phylogeny.
* Added class-based importer-related exceptions to exceptions.py.
* Removed old import_phylogeny function and other import-related functions from utils.py.


## v0.3 (2011.july.16):

* Added "exporter registry" to manage exporters.  Exporter registry makes it easier to add and remove exporters to the app with very little effort.  Exporter registry provides an interface to register available exporters and to subsequently get them, allowing code relying on exporters to be generic.
* Updated code that relied on exporters to use exporter registry instead.  Code no longer has knowledge of specific exporters; rather it works generically on any exporters exposed by exporter registry.
* Removed hard-coded references to specific exporters from app except in test cases.


## v0.2 (2011.july.15):

* Added class-based exporters (exporters.py).
* Added support throughout app for class-based exporters including:  view class PhylogenyExportView and export management command export-phylogeny.
* Added PhyloExporterUnsupportedTaxonAssignment exception to support class-based exporters.
* Removed old get_phylogeny and export_phylogeny functions from utils.py.
* Updated export management command and export view to use class-based exporters
* Moved all tests into tests/ folder
* Added tests for class-based exporters
* Removed old tests.py as tests are now contained in folder tests/


## v0.1 (2011.july.08):

* Initial release.
