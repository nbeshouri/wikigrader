#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='wikigrader',
      version='0.1',
      description='TODO',
      python_requires='>=3.6',
      author='Nicholas Beshouri',
      author_email='nbeshouri@gmail.com',
      packages=['wikigrader'],
      package_data={'wikigrader': ['data/*.pickle', 'data/*.hdf5']},
      include_package_data=True,
      zip_safe=False, 
      install_requires=['pandas', 'numpy', 'bs4', 'sklearn', 'keras', 'click', 'joblib'],
      entry_points={'console_scripts': ['wikigrader=wikigrader.command_line:cli']})
