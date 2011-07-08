# Django Phylogeny

Django Phylogeny is an app for working with phylogenetic trees in the Django web
development framework.


## Installation

### Official Release

Official releases are available at:
	
	https://github.com/randallmorey/django-phylogeny

Download the latest distribution archive, unarchive it, and run:

   python setup.py install

...and the package will install automatically.

### Development Branch

You may wish to clone the development version of the repository to receive the latest and greatest.  Please note that the development version may be unstable and should not be used in production.

	git clone https://github.com/randallmorey/django-phylogeny.git
	cd django-phylogeny
	git checkout -t -b develop origin/develop

Add the django-phylogeny/ folder to your `PYTHONPATH`.


## Requirements

* [Python 2.6 or newer](http://www.python.org/)
* [Django 1.3 or newer](http://www.djangoproject.com/)
* [Biopython 1.57 or newer](http://biopython.org/wiki/Biopython)
* [Django MPTT](https://github.com/django-mptt/django-mptt/)


## Using Django Phylogeny in a Project

Installing Django Phylogeny in your project is easy:

1. Install requirements (see above) somewhere on your `PYTHON_PATH`.
2. Place `phylogeny` into `INSTALLED_APPS` in `settings.py`.
3. Run `./manage.py syncdb`.


## Translatable Fields in Django Phylogeny

Django Phylogeny supports multiple languages and automatically integrates with [django-modeltranslation](http://code.google.com/p/django-modeltranslation/) (when available).

1. Install django-modeltranslation into your Python path.
2. Place `modeltranslation` into `INSTALLED_APPS` in `settings.py`.  Be sure to place this app _before_ `phylogeny`.
3. Add a `translation.py` file to your project folder with at least the following:
	
	from phylogeny import translation

4. Let django-modeltranslation know about your translations by adding to `settings.py`:
	
	MODELTRANSLATION_TRANSLATION_REGISTRY = 'trees.translation'

5. Specify which languages to enable as you normally would in the `LANGUAGES` setting.  For example:
	
	LANGUAGES = (
		('en', 'English'),
		('pt-br', 'Brazilian Portuguese'),
		('es', 'Spanish'),
	)


**Caution**:  django-modeltranslation alters fields on Django Phylogeny models at runtime.  If you intend to use Django Phylogeny with translatable fields, be sure to setup both django-modeltranslation and Django Phylogeny _before_ running the first `syncdb` command.  Adding django-modeltranslation after syncing the database will result in runtime exceptions, since the admin will attempt to access extra fields that don't exist in your database.  If you install django-modeltranslation to an existing project, you will need a schema migration tool such as [django-south](http://south.aeracode.org/docs/).
