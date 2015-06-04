#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://pdsview.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pdsview',
    version='0.1.0',
    description='Python PDS Image Viewer',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Austin Godber',
    author_email='godber@asu.edu',
    url='https://github.com/asu-bell-group/pdsview',
    packages=[
        'pdsview',
    ],
    package_dir={'pdsview': 'pdsview'},
    include_package_data=True,
    install_requires=[
        'ginga>=2.1',
    ],
    license='MIT',
    zip_safe=False,
    keywords='pdsview',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    entry_points={
        'console_scripts': [
            'pdsview = pdsview.pdsview:main'
        ],
    }
)
