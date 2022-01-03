# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from .. import persons
from .dbasterisk import DbAsterisk
from .asteriskfake_test import AsteriskFake_Test

class DbAsterisk_Test(AsteriskFake_Test):

    def setupPbx(self):
        self.tempdb = Path('dbasterisk_test.sqlite')
        try: self.tempdb.unlink()
        except: pass

        return DbAsterisk("sqlite", str(self.tempdb.resolve()), create_db=True)

    def tearDownPbx(self):
        try: self.tempdb.unlink()
        except: pass

    # This is not empty, it shares tests with AsteriskFake_Test


# vim: ts=4 sw=4 et
