from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='lcctool',
      version=version,
      description="Tool to manage Lifecycle Controller",
      long_description="""This is the long description of the tool to manage Lifecycle Controller""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='dell',
      author='Michael Brown',
      author_email='Michael_E_Brown@Dell.com',
      url='',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data = { 'lcctool': ['pkg/lcctool.ini',] },
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [ 'lcctool = lcctool.lcctool_cli:main', ],
        'lcctool_cli_extensions': [
            'sample = stdcli.plugins.builtin:SamplePlugin',
            'dump-config = stdcli.plugins.builtin:DumpConfigPlugin',
            'raccfg = lcctool.plugins.raccfg:RacCfg',
            'sample-raccfg-test = lcctool.plugins.raccfg:SampleTestRacCfg',
            'power-ctl = lcctool.plugins.power:PowerPlugin',
            ],
        },
      )
