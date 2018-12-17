#!/usr/bin/env python

# Author(s):  PB
# Maintainer: PB
# Created:    20181216
# License:    (c) 2018 HRDAG, GPL-v2 or greater
# ============================================
#
# makr/setup.py
#

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='makr',
      version='0.1-dev',
      description='make wrapper for principled data processing',
      url='https://github.com/HRDAG/makr',
      author='Patrick Ball',
      author_email='info@hrdag.org',
      setup_requires=['pytest-runner',],
      tests_require=['pytest',],
      license='GPL-v2 or newer',
      packages=['makr'],
      zip_safe=True)

# done.
