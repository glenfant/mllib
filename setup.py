# -*- coding: utf-8 -*-
"""\
=====
mllib
=====

A REST client for MarkLogic 8
"""

from setuptools import setup, find_packages
import os, sys

version = '1.0.0.dev0'

this_directory = os.path.abspath(os.path.dirname(__file__))

def read(*names):
    return open(os.path.join(this_directory, *names), 'r').read().strip()

long_description = '\n\n'.join(
    [read(*paths) for paths in (('README.rst',),
                               ('docs', 'contributors.rst'),
                               ('docs', 'changes.rst'))]
    )
dev_require = ['Sphinx']
if sys.version_info < (2, 7):
    dev_require += ['unittest2']

install_requires = ['setuptools', 'requests']
if sys.version_info < (3, 4):
    install_requires += ['enum34']

setup(name='mllib',
      version=version,
      description="A REST client for MarkLogic 8",
      long_description=long_description,
      # FIXME: Add more classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Documentation",
          "Topic :: Database :: Front-Ends",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent"
          ],
      keywords='',  # FIXME: Add whatefer fits
      author='Gilles Lenfant',
      author_email='gilles.lenfant@alterway.fr',
      url='http://pypi.python.org/pypi/mllib',
      license='MIT',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          },
      tests_require=dev_require,
      test_suite='tests.all_tests',
      extras_require={
          'dev': dev_require
      })
