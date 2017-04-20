# -*- coding: utf-8 -*-

import unittest
from callinfo import CallInfo
import ooop
try:
    import dbconfig
except ImportError:
    dbconfig = None
from yamlns import namespace as ns
    
@unittest.skipIf(not dbconfig or not dbconfig.ooop,
    "Requires configuring dbconfig.ooop")
class CallInfo_Test(unittest.TestCase):

    def setUp(self):
        pass

    def ns(self,content):
	return ns.loads(content)

    @classmethod
    def setUpClass(cls):
        cls.O = ooop.OOOP(**dbconfig.ooop)

    def test_searchAddressByPhone_whenMatchesNone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByPhone('badphone')
        self.assertEqual(ids, [])

    def test_searchAddressByPhone_whenMatchesOnePhone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByPhone('933730976')
        self.assertEqual(ids, [12073])

    def test_searchAddressByPhone_whenMatchesMoreThanOnePhone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByPhone('659509872')
        self.assertEqual(ids, [2286, 42055, 43422])

    def test_searchAddressByMobile_whenMatchesNone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByMobile('badphone')
        self.assertEqual(ids, [])

    def test_searchAddressByMobile_whenMatchesOnePhone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByMobile('699515879')
        self.assertEqual(ids, [34])

    def test_searchAddressByMobile_whenMatchesMoreThanOnePhone(self):
        info = CallInfo(self.O)
        ids = info.searchAddresByMobile('630079522')
        self.assertEqual(ids, [33,42])

    def test_searchPartnerByAddressId_whenMatchesNone(self):
        info = CallInfo(self.O)
        partner_ids = info.searchPartnerByAddressId([999999999])
        self.assertEqual(partner_ids,[])

    def test_searchPartnerByAddressId_whenMatchesOnePartner(self):
        info = CallInfo(self.O)
        partner_ids = info.searchPartnerByAddressId([12073])
        self.assertEqual(partner_ids, [11709])

    def test_searchPartnerByAddressId_whenEmpty(self):
        info = CallInfo(self.O)
        partner_ids = info.searchPartnerByAddressId([])
        self.assertEqual(partner_ids, [])

    def test_searchPartnerByAddressId_whenAddreswithNoPartner(self):
        info = CallInfo(self.O)
        partner_ids = info.searchPartnerByAddressId([67234])
        self.assertEqual(partner_ids, [])

    def test_searchPartnerByAddressId_whenMatchesMoreThanOnePartner(self):
        info = CallInfo(self.O)
        partner_ids = info.searchPartnerByAddressId([2286, 42055, 43422])
        self.assertEqual(partner_ids, [410, 39933, 41193])

    def test_searchPartnerByAddressId_whenMatchesMoreThanOnePartnerAndNotFound(self):
        info = CallInfo(self.O)
        partner_ids = info.searchPartnerByAddressId([2286, 42055, 43422, 999999999])
        self.assertEqual(partner_ids, [410, 39933, 41193])

    '''def test_getPartnerData_whenEmpty(self):
	info = CallInfo(self.O)
	partner_data = info.getPartnerData([0])
	self.assertEqual(partner_data, self.ns("""partner: 
  lang:
  name:
  city:
  email:
  polisses_ids:
  provincia:
 """))'''
	

    def test_getPartnerData_whenMatchesOne(self):
	info = CallInfo(self.O, anonimize=True)
	partner_data = info.getPartnerData([410])
        self.assertEqual(partner_data, self.ns("""partner:
  'lang': 'ca_ES' 
  'name': 'Ju...ol'
  'city': 'Vilanova de Bellpuig'
  'email': 'or...op'
  'polisses_ids': 
  - 155
  - 56427
  'provincia': 'Lleida'
"""))

unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et
