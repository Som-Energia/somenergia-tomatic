# -*- coding: utf-8 -*-

import unittest
from callinfoE import CallInfo
import ooop
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
        cls.E = erppeek.Client(**dbconfig.erppeek)
                
    def test_addressByPhone_whenMatchesNone(self):
        info = CallInfo(self.O, self.E)
        ids = info.addressByPhone('badphone')
        self.assertEqual(ids, [])

    def test_addressByPhone_whenMatchesOnePhone(self):
        info = CallInfo(self.O, self.E)
        ids = info.addressByPhone('933730976')
        self.assertEqual(ids, [12073])

    def test_addressByPhone_whenMatchesMoreThanOnePhone(self):
        info = CallInfo(self.O, self.E)
        ids = info.addressByPhone('659509872')
        self.assertEqual(ids, [2286, 42055, 43422])

    def test_addressByPhone_whenMatchesOneMobile(self):
        info = CallInfo(self.O, self.E)
        ids = info.addressByPhone('699515879')
        self.assertEqual(ids, [34])

    def test_addressByPhone_whenMatchesMoreThanOneMobile(self):
        info = CallInfo(self.O, self.E)
        ids = info.addressByPhone('630079522')
        self.assertEqual(ids, [33,42])

    def test_partnerByAddressId_whenMatchesNone(self):
        info = CallInfo(self.O, self.E)
        partner_ids = info.partnerByAddressId([999999999])
        self.assertEqual(partner_ids,[])

    def test_partnerByAddressId_whenMatchesOnePartner(self):
        info = CallInfo(self.O, self.E)
        partner_ids = info.partnerByAddressId([12073])
        self.assertEqual(partner_ids, [11709])

    def test_spartnerByAddressId_whenEmpty(self):
        info = CallInfo(self.O, self.E)
        partner_ids = info.partnerByAddressId([])
        self.assertEqual(partner_ids, [])

    def test_partnerByAddressId_whenAddreswithNoPartner(self):
        info = CallInfo(self.O, self.E)
        partner_ids = info.partnerByAddressId([67234])
        self.assertEqual(partner_ids, [])

    def test_partnerByAddressId_whenMatchesMoreThanOnePartner(self):
        info = CallInfo(self.O, self.E)
        partner_ids = info.partnerByAddressId([2286, 42055, 43422])
        self.assertEqual(partner_ids, [410, 39933, 41193])

    def test_partnerByAddressId_whenMatchesMoreThanOnePartnerAndNotFound(self):
        info = CallInfo(self.O, self.E)
        partner_ids = info.partnerByAddressId([2286, 42055, 43422, 999999999])
        self.assertEqual(partner_ids, [410, 39933, 41193])

    def test_partnerInfo_whenMatchesOne(self):
        info = CallInfo(self.O, self.E, anonymize=True)
        partner_data = info.partnerInfo([410])
        self.assertNsEqual(partner_data, """\
            partner:
                'lang': 'ca_ES' 
                'name': '...iol'
                'city': 'Vilanova de Bellpuig'
                'email': '...oop'
                'id_soci': '...367'
                'polisses_ids': 
                - 155
                - 56427
                'provincia': 'Lleida'
            """)

    def test_partnersInfo_whenMatchesOne(self):
        info = CallInfo(self.O, self.E, anonymize=True)
        partner_data = info.partnersInfo([410])
        self.assertNsEqual(partner_data, """\
            partners:
              - '...iol':
                  'lang': 'ca_ES'
                  'city': 'Vilanova de Bellpuig'
                  'provincia': 'Lleida'
                  'name': '...iol'
                  'id_soci': '...367'
                  'email': '...oop'       
                  'polisses' :
                    - 'polissa': 
                        'baixa': ''
                        'cups': '...F0F'
                        'alta': '2011-11-19'
                        'estat': 'activa'
                        'potencia': 3.45
                        'tarifa': '2.0DHA'                    
                    - 'polissa':
                        'baixa': ''
                        'cups': '...H0F'
                        'alta': '2015-07-17'
                        'estat': 'activa'
                        'potencia': 1.15
                        'tarifa': '2.0A'                    
            """)
        
    def test_polisseInfo_whenAskNone(self):
        info = CallInfo(self.O ,self.E, anonymize=True)
        polisse_data = info.polisseInfo([])
        self.assertNsEqual(polisse_data, """\
            polisses: []
            """)
        
    def test_polisseInfo_whenAskOne(self):
        info = CallInfo(self.O, self.E, anonymize=True)
        polisse_data = info.polisseInfo([155])
        self.assertNsEqual(polisse_data, """\
            polisses:
             - polissa:
                 baixa: ''
                 cups: ...F0F
                 alta: '2011-11-19'
                 estat: activa
                 potencia: 3.45
                 tarifa: 2.0DHA
            """)

    def test_polisseInfo_whenAskMore(self):
        info = CallInfo(self.O, self.E, anonymize=True)
        polisse_data = info.polisseInfo([155,250])
        self.assertNsEqual(polisse_data, """\
            polisses:
             - polissa:
                 baixa: ''
                 cups: ...F0F
                 alta: '2011-11-19'
                 estat: activa
                 potencia: 3.45
                 tarifa: 2.0DHA
             - polissa:
                 baixa: ''
                 cups: ...P0F
                 alta: '2012-03-29'
                 estat: activa
                 potencia: 3.45
                 tarifa: 2.0A
            """)
        
    def test_getByPhone_global(self):
        info = CallInfo(self.O ,self.E)
        data = info.getByPhone("630079522")
        self.assertB2BEqual(data.dump())

unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et
