# Django Phylogeny Changelog


## v0.3.0 (2011.july.16):

* Added "exporter registry" to manage exporters.  Exporter registry makes it easier to add and remove exporters to the app with very little effort.  Exporter registry provides an interface to register available exporters and to subsequently get them, allowing code relying on exporters to be generic.
* Updated code that relied on exporters to use exporter registry instead.  Code no longer has knowledge of specific exporters; rather it works generically on any exporters exposed by exporter registry.
* Removed hard-coded references to specific exporters from app except in test cases.

## v0.2.0 (2011.july.15):

* Added class-based exporters (exporters.py).
* Added support throughout app for class-based exporters including:  view class PhylogenyExportView and export management command export-phylogeny.
* Added PhyloExporterUnsupportedTaxonAssignment exception to support class-based exporters.
* Removed old get_phylogeny and export_phylogeny functions from utils.py.
* Updated export management command and export view to use class-based exporters
* Moved all tests into tests/ folder
* Added tests for class-based exporters
* Removed old tests.py as tests are now contained in folder tests/


## v0.1.0 (2011.july.08):

* Initial release.
