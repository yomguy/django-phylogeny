from setuptools import setup, find_packages


version_tuple = __import__('phylogeny').VERSION
version = '.'.join(version_tuple)


setup(
	name='django-phylogeny',
	version=version,
	description ='Phylogenetic Trees for Django',
	author='Randall Morey',
	url='http://github.com/randallmorey/django-phylogeny',
	packages=find_packages(),
	zip_safe=False
)
