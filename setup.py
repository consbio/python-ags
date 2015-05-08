import os
from distutils.core import setup


long_description = 'A client interface to the REST API on ArcGIS Server 10.2.x'


if os.path.exists('README.md'):
    try:
        # Use pypandoc to convert markdown readme to reStructuredText as required by pypi
        # Requires pandoc to be installed.  See: http://johnmacfarlane.net/pandoc/installing.html
        from pypandoc import convert
        read_md = lambda f: convert(f, 'rst', format='md')
        long_description = read_md('README.md')
    except:
        pass


setup(
    name='python-ags',
    description='A client interface to the REST API on ArcGIS Server 10.2.x',
    long_description=long_description,
    keywords='arcgis ags',
    version='0.2.3.1',
    packages=['ags', 'ags.admin', 'ags.admin.services'],
    requires=["requests"],
    url='https://bitbucket.org/databasin/python-ags',
    author='Data Basin',
    author_email='databasinadmin@consbio.org',
    maintainer='Data Basin',
    maintainer_email='databasinadmin@consbio.org',
    license='BSD'
)