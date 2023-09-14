#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys
from setuptools import setup, find_packages
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
    packages=find_packages(exclude=['*[tT]est*']),
    scripts=[
        'scripts/areavoip_callapi.py',
        'scripts/areavoip_dumpstats.sh',
        'scripts/execution_example.sh',
        'scripts/crontab-dailyreport.sh',
        'scripts/crontab-warnturn.sh',
        'scripts/crontab-launchtimetable.sh',
        'runhere',
        'scripts/tomatic_api.py',
        'scripts/tomatic_busy.py',
        'scripts/tomatic_callinfo.py',
        'scripts/tomatic_calls.py',
        'scripts/tomatic_dailyreport.py',
        'scripts/tomatic_extensions.py',
        'scripts/tomatic_mergeshifts.py',
        'scripts/tomatic_resetshiftcredit.sh',
        'scripts/tomatic_retrieve.py',
        'scripts/tomatic_rtqueue.py',
        'scripts/tomatic_timetable.py',
        'scripts/tomatic_timetablelauncher.py',
        'scripts/tomatic_says.py',
        'scripts/tomatic_scheduler.py',
        'scripts/tomatic_shiftload.py',
        'scripts/tomatic_stats.py',
        'scripts/tomatic_uploadcases.py',
        'scripts/tomatic_uploadtimetable.py',
        ],
    install_requires=[
        'setuptools>=20.4',
        'MarkupSafe',
        'somutils>=1.9', # use of enterContext
        'tomato-cooker>=0.4.0', # api changed
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
        'elasticsearch<8', # 8 version is incompatible with irontec server
        'ics<0.8', # icalendar generation. 0.8 changes interface and not yet available in all Pythons
        'itsdangerous', # auth
        'authlib<1.0', # auth
        'httpx<1', # auth, 1.0 changes API, incompatible with fastapi 0.95.0 and earlier
        'python-jose[cryptography]', # auth
        'charset-normalizer<3', # request and httpio complains once 3.x is out
        'httplib2', # Google chat code
        'backports.zoneinfo; python_version < "3.9"', # Py3.8 support for Py3.9 zoneinfo
        'pandas',
        'matplotlib',
    #],
    #tests_require=[
        'pytest-cov',
        'pytest',
        'coverage',
        'b2btest',
        'lxml',
        'erppeek',
        'ERPPeek-WST',
        'mock',
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
