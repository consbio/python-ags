from distutils.core import setup
setup(
    name='python-ags',
    version='0.2.1',
    packages=['ags', 'ags.admin', 'ags.admin.services'],
    requires=["requests"]
)