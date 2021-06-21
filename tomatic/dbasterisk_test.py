# -*- coding: utf-8 -*-

import unittest
import os
from pony.orm import db_session, rollback
from pathlib import Path
from yamlns import namespace as ns
from . import persons
from .dbasterisk import DbAsterisk
from .asteriskfake_test import AsteriskFake_Test

class DbAsterisk_Test(AsteriskFake_Test):

    def setupPbx(self):
        try: Path('tomatic/demo.sqlite').unlink()
        except: pass

        return DbAsterisk("sqlite", 'demo.sqlite', create_db=True)
    def tearDownPbx(self):
        try: Path('tomatic/demo.sqlite').unlink()
        except: pass

    # This is not empty, it shares tests with AsteriskFake_Test


# vim: ts=4 sw=4 et
