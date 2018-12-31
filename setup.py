#!/usr/bin/env python

# Author(s):  PB
# Maintainer: PB
# Created:    20181216
# License:    (c) 2018 HRDAG, GPL-v2 or greater
# ============================================
#
# makr/setup.py
#
import sys
from setuptools import setup

if sys.version_info < (3, 7):
    sys.exit("python 3.7 or newer is required")


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='makr',
      version='0.1-alpha',
      description='make wrapper for principled data processing',
      url='https://github.com/HRDAG/makr',
      author='Patrick Ball',
      author_email='info@hrdag.org',
      python_requires='>=3.7',
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      scripts=['bin/makr'],
      license='GPL-v2 or newer',
      packages=['makr'],
      zip_safe=True)

# done.
