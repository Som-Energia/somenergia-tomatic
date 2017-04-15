# -*- coding: utf-8 -*-

import unittest
from callinfo import CallInfo
import ooop
try:
    import dbconfig
except ImportError:
    dbconfig = None

@unittest.skipIf(not dbconfig or not dbconfig.ooop,
    "Requires configuring dbconfig.ooop")
class CallInfo_Test(unittest.TestCase):

    def setUp(self):
        print "setup"

    @classmethod
    def setUpClass(cls):
        print "classSetUp"
        cls.O = ooop.OOOP(**dbconfig.ooop)

    def test_searchAddressByPhone_whenMatchesNone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByPhone('badphone')
        self.assertEqual(ids, [])

    def test_searchAddressByPhone_whenMatchesOnePhone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByPhone('933730976')
        self.assertEqual(ids, [12073])



unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et
