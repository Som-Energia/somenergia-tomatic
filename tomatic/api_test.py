# -*- coding: utf-8 -*-

import b2btest
import unittest
from yamlns import namespace as ns
from datetime import datetime

from . import api

def setNow(year,month,day,hour,minute):
    api.now=lambda:datetime(year,month,day,hour,minute)

class Api_Test(unittest.TestCase):

    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        self.maxDiff = None
        self.b2bdatapath = "testdata"

if __name__ == "__main__":

    import sys
    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True

    unittest.main()

# vim: ts=4 sw=4 et
