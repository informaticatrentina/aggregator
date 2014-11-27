# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author: Daniele Pizzolli <daniele@ahref.eu>
#
# This file is part of the aggregator project.
#
# This file can not be copied and/or distributed without the express
# permission of <ahref Foundation.
#
###############################################################################


from setuptools import setup

with open('requirements/base.txt') as f:
     requirements_base = f.read().splitlines()

with open('requirements/test.txt') as f:
    requirements_test = f.read().splitlines()

setup(
    name='Aggregator',
    version=open('version.txt').read().strip(),
    author = 'Daniele Pizzolli',
    author_email='daniele@ahref.eu',
    packages=['aggregator', 'aggregator.test'],
    # namespace_packages=['aggregator'],
    keywords = 'aggregator',
    url='http://gitlab.ahref.eu/core/aggregator',
    license='Proprietary License',
    long_description=open('README.rst').read(),
    description = ('aggregator is the core component of <ahref platforms'),
    entry_points='''
        [console_scripts]
        aggregator = aggregator.manage:main
        ''',
    # To skip problems of local eggs we make fat requirements:
    # http://stackoverflow.com/questions/1843424/setup-py-test-egg-install-location
    install_requires=requirements_base + requirements_test,
    include_package_data=True,
    test_suite='nose.collector',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
