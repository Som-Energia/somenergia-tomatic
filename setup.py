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
    test_suite = 'tomatic',
    scripts=[
        'schedulehours.py',
        'tomatic_api.py',
        ],
    install_requires=[
        'somutils',
        'yamlns',
        'consolemsg',
        'parse',
        'flask',
        'py-Asterisk',
        'paramiko',
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

