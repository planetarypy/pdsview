#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

setup(
    name='pdsview',
    version='0.5.0',
    description="PDS Image Viewer",
    long_description=readme + '\n\n' + history,
    author="PlanetaryPy Developers",
    author_email='contact@planetarypy.com',
    url='https://github.com/planetarypy/pdsview',
    packages=[
        'pdsview',
    ],
    package_dir={'pdsview':
                 'pdsview'},
    include_package_data=True,
    install_requires=[
        'ginga==2.6.0',
        'planetaryimage>=0.5.0',
        'matplotlib>=1.5.1',
        'QtPy>=1.2.1'
    ],
    license="BSD",
    zip_safe=False,
    keywords='pdsview',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'pdsview = pdsview.pdsview:cli'
        ],
    }
)
