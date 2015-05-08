from distutils.core import setup

setup(
    name='python-ags',
    description='A client interface to the REST API on ArcGIS Server 10.2.x',
    keywords='arcgis ags',
    version='0.2.3',
    packages=['ags', 'ags.admin', 'ags.admin.services'],
    requires=["requests"],
    url='https://bitbucket.org/databasin/python-ags',
    author='Data Basin',
    author_email='databasinadmin@consbio.org',
    maintainer='Data Basin',
    maintainer_email='databasinadmin@consbio.org',
    license='BSD'
)