# Django Phylogeny Changelog


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
