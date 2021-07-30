# -*- encoding: utf-8 -*-

import unittest
import os
from unittest.case import skip
from erppeek_wst import ClientWST
from xmlrpc import client as xmlrpclib
from yamlns import namespace as ns
from .crmcase import CrmCase

try:
    import dbconfig
except ImportError:
    dbconfig = None

@unittest.skipIf(os.environ.get("TRAVIS"),
    "Database not available in Travis")
@unittest.skipIf(
    not dbconfig or not dbconfig.erppeek,
    "Requires configuring dbconfig.erppeek"
)
class Claims_Test(unittest.TestCase):

    def setUp(self):
        if not dbconfig:
            return
        if not dbconfig.erppeek:
            return
        self.erp = ClientWST(**dbconfig.erppeek)
        self.erp.begin()

    def tearDown(self):
        try:
            self.erp.rollback()
            self.erp.close()
        except xmlrpclib.Fault as e:
            if 'transaction block' not in e.faultCode:
                raise

    @skip("there are nocategories in testing")
    def test_getCrmCategories(self):
        crm_case = CrmCase(self.erp)
        crm_categories = crm_case.get_crm_categories()
        categories = ns.load('b2bdata/categories_b2b.yaml')
        self.assertEqual(crm_categories, categories)


# vim: et ts=4 sw=4