# -*- coding: utf-8 -*-

import unittest
from callinfo import CallInfo
import erppeek
try:
    import dbconfig
except ImportError:
    dbconfig = None
from yamlns import namespace as ns
import b2btest

@unittest.skipIf(not dbconfig or not dbconfig.erppeek,
    "Requires configuring dbconfig.erppeek")
class CallInfo_Test(unittest.TestCase):

    from testutils import assertNsEqual

    def setUp(self):
        self.maxDiff = None
        self.b2bdatapath = "testdata"

    def ns(self,content):
        return ns.loads(content)

    @classmethod
    def setUpClass(cls):
        cls.O = erppeek.Client(**dbconfig.erppeek)

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

    def test_partnerByAddressId_whenMatchesNone(self):
        info = CallInfo(self.O)
        partner_ids = info.partnerByAddressId([999999999])
        self.assertEqual(partner_ids,[])

    def test_partnerByAddressId_whenMatchesOnePartner(self):
        info = CallInfo(self.O)
        partner_ids = info.partnerByAddressId([12073])
        self.assertEqual(partner_ids, [11709])

    def test_spartnerByAddressId_whenEmpty(self):
        info = CallInfo(self.O)
        partner_ids = info.partnerByAddressId([])
        self.assertEqual(partner_ids, [])

    def test_partnerByAddressId_whenAddreswithNoPartner(self):
        info = CallInfo(self.O)
        partner_ids = info.partnerByAddressId([67234])
        self.assertEqual(partner_ids, [])

    def test_partnerByAddressId_whenMatchesMoreThanOnePartner(self):
        info = CallInfo(self.O)
        partner_ids = info.partnerByAddressId([2286, 42055, 43422])
        self.assertEqual(partner_ids, [410, 39933, 41193])

    def test_partnerByAddressId_whenMatchesMoreThanOnePartnerAndNotFound(self):
        info = CallInfo(self.O)
        partner_ids = info.partnerByAddressId([2286, 42055, 43422, 999999999])
        self.assertEqual(partner_ids, [410, 39933, 41193])

    def test_partnerInfo_whenMatchesOne(self):
        info = CallInfo(self.O, anonymize=True)
        data = self.O.ResPartner.read([410],[
            'city',
            'www_email',
            'www_provincia',
            'polisses_ids',
            'name',
            'ref',
            'lang',
        ])[0]
        partner_data = info.partnerInfo(ns(data))
        self.assertNsEqual(partner_data, """\
            lang: ca_ES
            name: ...iol
            city: Vilanova de Bellpuig
            email: ...oop
            id_soci: ...367
            contracts_ids:
            - 155
            - 56427
            state: Lleida
            """)

    def test_partnersInfo_whenMatchesOne(self):
        info = CallInfo(self.O, anonymize=True)
        partner_data = info.partnersInfo([410])
        self.assertNsEqual(partner_data, """\
            partners:
            -
              lang: ca_ES
              city: Vilanova de Bellpuig
              state: Lleida
              name: ...iol
              id_soci: ...367
              email: ...oop
              contracts:
              - 
                end_date: ''
                cups: ...F0F
                start_date: '2011-11-19'
                state: activa
                power: 3.45
                fare: 2.0DHA
              -
                end_date: ''
                cups: ...H0F
                start_date: '2015-07-17'
                state: activa
                power: 1.15
                fare: 2.0A
            """)

    def test_contractInfo_whenAskNone(self):
        info = CallInfo(self.O, anonymize=True)
        contractsData = info.contractInfo([0])
        self.assertNsEqual(contractsData, """\
            contracts: []
            """)

    def test_contractInfo_whenAskOne(self):
        info = CallInfo(self.O, anonymize=True)
        contractsData = info.contractInfo([155])
        self.assertNsEqual(contractsData, """\
            contracts:
            -
              end_date: ''
              cups: ...F0F
              start_date: '2011-11-19'
              state: activa
              power: 3.45
              fare: 2.0DHA
            """)

    def test_contractInfo_whenAskMore(self):
        info = CallInfo(self.O, anonymize=True)
        contractsData = info.contractInfo([155,250])
        self.assertNsEqual(contractsData, """\
            contracts:
            -
              start_date: '2011-11-19'
              end_date: ''
              cups: ...F0F
              state: activa
              power: 3.45
              fare: 2.0DHA
            -
              start_date: '2012-03-29'
              end_date: ''
              cups: ...P0F
              state: activa
              power: 3.45
              fare: 2.0A
            """)

    def test_getByPhone_global(self):
        info = CallInfo(self.O)
        data = info.getByPhone("630079522")
        self.assertB2BEqual(data.dump())

unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et
