#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys
from setuptools import setup
from tomatic import __version__
readme = open("README.md").read()

setup(
    name = "tomatic",
    version = __version__,
    description = "Phone Support Helper",
    author = "David García Garzón",
    author_email = "david.garcia@somenergia.coop",
    url = 'https://github.com/Som-Energia/somenergia-tomatic',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    license = 'GNU Affero General Public License v3 or later (GPLv3+)',
    scripts=[
        'scripts/areavoip_callapi.py',
        'scripts/areavoip_dailyreport.py',
        'scripts/execution_example.sh',
        'scripts/crontab-dailyreport.sh',
        'scripts/crontab-warnturn.sh',
        'runhere',
        'scripts/tomatic_api.py',
        'scripts/tomatic_busy.py',
        'scripts/tomatic_callinfo.py',
        'scripts/tomatic_calls.py',
        'scripts/tomatic_extensions.py',
        'scripts/tomatic_mergeshifts.py',
        'scripts/tomatic_resetshiftcredit.sh',
        'scripts/tomatic_retrieve.py',
        'scripts/tomatic_rtqueue.py',
        'scripts/tomatic_says.py',
        'scripts/tomatic_scheduler.py',
        'scripts/tomatic_shiftload.py',
        'scripts/tomatic_uploadcases.py',
        'scripts/tomatic_uploadtimetable.py',
        ],
    install_requires=[
        'setuptools>=20.4',
        'MarkupSafe',
        'somutils',
        'yamlns',
        'consolemsg',
        'parse',
        'jsmin',
        'py-Asterisk',
        'paramiko',
        'python-slugify',
        'deansi',
        #'ooop==0.2.2-xt',
        'PyMySQL',
        'click',
        'decorator',
        'requests',
        'ERPpeek',
        'psutil',
        'pony',
        'emili',
        'fastapi',
        'python-multipart', # formdata in fastapi
        'uvicorn[standard]', # server for fastapi (standard for websockets)
        'aiofiles', # Static files for fastapi
        'hangups',
    #],
    #tests_require=[
        'nose',
        'rednose',
        'coverage',
        'b2btest',
        'lxml',
        'wavefile',
        'erppeek',
        'ERPPeek-WST',
    ],
    test_suite = 'nose.collector',
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
