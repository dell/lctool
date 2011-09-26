from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='lcc_wsman',
      version=version,
      description="Tool to get data from Dell Lifecycle Controller"
      long_description="""This is the long description""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='dell',
      author='Michael Brown',
      author_email='Michael_E_Brown@Dell.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data = { 'lcc_wsman': ['*.xml',] },
      zip_safe=False,
      entry_points={
        'console_scripts': [ 'lcctool = lcc_wsman.cli:main', ],
        'lcctool_cli_extensions': [
            'sample = stdcli.plugins.builtin:SamplePlugin',
            ],
        },
      )
