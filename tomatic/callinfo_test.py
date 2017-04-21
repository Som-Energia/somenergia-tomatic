# -*- coding: utf-8 -*-

import unittest
from callinfo import CallInfo
import ooop
try:
    import dbconfig
except ImportError:
    dbconfig = None
from yamlns import namespace as ns
import b2btest
    
@unittest.skipIf(not dbconfig or not dbconfig.ooop,
    "Requires configuring dbconfig.ooop")
class CallInfo_Test(unittest.TestCase):

    def assertNsEqual(self, dict1, dict2):
        def parseIfString(nsOrString):
            if type(nsOrString) in (dict, ns):
                return nsOrString
            return ns.loads(nsOrString)

        def sorteddict(d):
            if type(d) not in (dict, ns):
                return d
            return ns(sorted(
                (k, sorteddict(v))
                for k,v in d.items()
                ))
        dict1 = sorteddict(parseIfString(dict1))
        dict2 = sorteddict(parseIfString(dict2))

        return self.assertMultiLineEqual(dict1.dump(), dict2.dump())

    def setUp(self):
        self.maxDiff = None
        self.b2bdatapath = "testdata"

    def ns(self,content):
        return ns.loads(content)

    @classmethod
    def setUpClass(cls):
        cls.O = ooop.OOOP(**dbconfig.ooop)

    def test_addressByPhone_whenMatchesNone(self):
        info = CallInfo(self.O)
        ids = info.addressByPhone('badphone')
        self.assertEqual(ids, [])

    def test_addressByPhone_whenMatchesOnePhone(self):
        info = CallInfo(self.O)
        ids = info.addressByPhone('933730976')
        self.assertEqual(ids, [12073])

    def test_addressByPhone_whenMatchesMoreThanOnePhone(self):
        info = CallInfo(self.O)
        ids = info.addressByPhone('659509872')
        self.assertEqual(ids, [2286, 42055, 43422])

    def test_addressByPhone_whenMatchesOneMobile(self):
        info = CallInfo(self.O)
        ids = info.addressByPhone('699515879')
        self.assertEqual(ids, [34])

    def test_addressByPhone_whenMatchesMoreThanOneMobile(self):
        info = CallInfo(self.O)
        ids = info.addressByPhone('630079522')
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

    def test_getPartnerData_whenMatchesOne(self):
        info = CallInfo(self.O, anonymize=True)
        partner_data = info.getPartnerData([410])
        self.assertNsEqual(partner_data, """\
            partner:
              'lang': 'ca_ES' 
              'name': 'Ju...ol'
              'city': 'Vilanova de Bellpuig'
              'email': 'or...op'
              'polisses_ids': 
              - 155
              - 56427
              'provincia': 'Lleida'
            """)

    def test_getByPhone(self):
        info = CallInfo(self.O)
        data = info.getByPhone("620471117")
        self.assertB2BEqual(data.dump())

    def test_getPolisseData(self):
        info = CallInfo(self.O)
        polisse_data = info.getPolisseData([155,56427])
        self.assertB2BEqual(polisse_data.dump())


unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et
