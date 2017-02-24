#!/usr/bin/env python

from distutils.core import setup

setup(name='telescope',
      version='1.0',
      description='TCSng telescope client class',
      author='Scott Swindell',
      author_email='scottswindell@email.arizona.edu',
	  py_modules = ['telescope', "minitel" ],
          package_dir = {'':'src'}
     )
