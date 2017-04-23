#!/usr/bin/env python
# -*- encoding: utf8 -*-

from setuptools import setup

readme = open("README.rst").read()

setup(
    name = "tomatic",
    version = "2.0",
    description = "Phone turns scheduler and shifter",
    author = "David García Garzón",
    author_email = "david.garcia@somenergia.coop",
    url = 'https://github.com/Som-Energia/somenergia-phonehours',
    long_description = readme,
    license = 'GNU General Public License v3 or later (GPLv3+)',
    test_suite = 'nose.collector',
    scripts=[
        'schedulehours.py',
        'tomatic_api.py',
        ],
    install_requires=[
        'setuptools==20.4',
        'somutils',
        'yamlns',
        'consolemsg',
        'parse',
        'Flask',
        'Flask-Assets',
        'Flask-Script',
        'jsmin',
        'py-Asterisk',
        'paramiko',
        'ooop', # TODO: Force Gisce Version
    #],
    #tests_require=[
        'nose',
        'rednose',
        'coverage',
        'b2btest',
        'lxml',
        'wavefile',
    ],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)

# vim: et ts=4 sw=4
