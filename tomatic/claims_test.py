# -*- encoding: utf-8 -*-

import unittest
import os
from consolemsg import error
from erppeek_wst import ClientWST
from yamlns import namespace as ns
from xmlrpc import client as xmlrpclib
from .claims import Claims
try:
    import dbconfig
except ImportError:
    dbconfig = None

def fkname(result, attrib):
    if not result[attrib]: return
    result[attrib] = result[attrib][1]

def anonymize(result, attrib):
    if not result[attrib]: return
    result[attrib] = '...'+result[attrib][-3:]

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
        self.maxDiff = None

    def tearDown(self):
        try:
            self.erp.rollback()
            self.erp.close()
        except xmlrpclib.Fault as e:
            if 'transaction block' not in e.faultCode:
                raise

    from yamlns.testutils import assertNsEqual

    def assertCrmCase(self, case_id, expected):
        if not expected:
            self.assertFalse(case_id)
            return
        self.assertTrue(case_id)
        result = ns(self.erp.CrmCase.read(case_id, [
            'section_id',
            'name',
            'canal_id',
            'polissa_id',
            'partner_id',
            'partner_address_id',
            'state',
            'user_id',
        ]))

        fkname(result, "section_id")
        fkname(result, "canal_id")
        fkname(result, "partner_id")
        fkname(result, "partner_address_id")
        fkname(result, "polissa_id")
        fkname(result, "user_id")
        anonymize(result, 'partner_id')
        anonymize(result, 'partner_address_id')

        self.assertNsEqual(ns(result), expected)


    def assertAtcCase(self, case_id, expected):
        if not expected:
            self.assertFalse(case_id)
            return
        self.assertTrue(case_id)
        result = ns(self.erp.GiscedataAtc.read(case_id, [
            'provincia',
            'total_cups',
            'cups_id',
            'subtipus_id',
            'reclamante',
            'resultat',
            'date',
            'email_from',
            'time_tracking_id',
        ]))

        fkname(result, "cups_id")
        fkname(result, "subtipus_id")
        fkname(result, "time_tracking_id")
        fkname(result, "provincia")
        anonymize(result, "email_from")

        self.assertNsEqual(ns(result), expected)

    def test_getAllClaims(self):
        claims = Claims(self.erp)
        reclamacions = claims.get_claims()
        Reclamacio = self.erp.GiscedataSubtipusReclamacio
        nombre_reclamacions = Reclamacio.count()
        self.assertEqual(len(reclamacions), nombre_reclamacions)

    def test_createAtcCase(self):
        case = ns.loads("""\
            date: '2021-11-11T15:13:39.998Z'
            person: gabriel
            reason: '[RECLAMACIONS] 003. INCIDENCIA EN EQUIPOS DE MEDIDA'
            partner: S001975
            contract: '0013117'
            procedente: ''
            improcedente: x
            solved: x
            user: RECLAMACIONS
            cups: ES0031405524910014WM0F
            observations: adfasd
        """)

        claims = Claims(self.erp)
        case_id = claims.create_atc_case(case)
        last_case_id = self.erp.GiscedataAtc.search()[0]
        self.assertAtcCase(case_id, """
            cups_id: ES0031405524910014WM0F
            date: '2021-11-11 15:13:39.998'
            email_from: ...oop
            id: {}
            provincia: Barcelona
            reclamante: '01'
            resultat: '02'
            subtipus_id: '003'
            time_tracking_id: Comercialitzadora
            total_cups: 1
        """.format(case_id))

    def test_createCrmCase(self):
        case = ns.loads("""\
            date: '2021-11-11T15:13:39.998Z'
            phone: ''
            person: gabriel
            reason: '[RECLAMACIONS] 003. INCIDENCIA EN EQUIPOS DE MEDIDA'
            partner: S001975
            contract: '0013117'
            user: RECLAMACIONS
            observations: adfasd
        """)
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            id: {}
            name: INCIDENCIA EN EQUIPOS DE MEDIDA
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: '0013117'
            section_id: Atenció al Client / RECLAMACIONS
            state: open
            user_id: false
        """.format(case_id))

    def test_createCrmCase_noContract(self):
        case = ns.loads("""\
            date: '2021-11-11T15:13:39.998Z'
            phone: ''
            person: gabriel
            reason: '[RECLAMACIONS] 003. INCIDENCIA EN EQUIPOS DE MEDIDA'
            partner: S001975
            contract: ''
            user: RECLAMACIONS
            observations: adfasd
        """)
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            id: {}
            name: INCIDENCIA EN EQUIPOS DE MEDIDA
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: False
            section_id: Atenció al Client / RECLAMACIONS
            state: open
            user_id: false
        """.format(case_id))

    def test_createCrmCase_noPartner(self):
        case = ns.loads("""\
            date: '2021-11-11T15:13:39.998Z'
            phone: ''
            person: gabriel
            reason: '[RECLAMACIONS] 003. INCIDENCIA EN EQUIPOS DE MEDIDA'
            partner: ''
            contract: ''
            user: RECLAMACIONS
            observations: adfasd
        """)
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            id: {}
            name: INCIDENCIA EN EQUIPOS DE MEDIDA
            partner_address_id: False
            partner_id: False
            polissa_id: False
            section_id: Atenció al Client / RECLAMACIONS
            state: open
            user_id: false
        """.format(case_id))


# vim: et ts=4 sw=4
