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
        self.assertEqual(case_id, last_case_id)

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
        self.assertTrue(case_id)
        crmcase = ns(self.erp.CrmCase.read(case_id, [
            'section_id',
            'name',
            'canal_id',
            'polissa_id',
            'partner_id',
            'partner_address_id',
            'state',
            'user_id',
        ]))
        def anonymize(text): return "..."+text[-3:]

        crmcase.section_id = crmcase.section_id[1]
        crmcase.canal_id = crmcase.canal_id[1]
        crmcase.partner_id = anonymize(crmcase.partner_id[1])
        crmcase.partner_address_id = anonymize(crmcase.partner_address_id[1])
        crmcase.polissa_id = crmcase.polissa_id[1]
        #crmcase.user_id = crmcase.user_id[1]
        self.assertNsEqual(ns(crmcase), """\
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



# vim: et ts=4 sw=4
