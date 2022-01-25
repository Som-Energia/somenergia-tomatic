# -*- encoding: utf-8 -*-

import unittest
import b2btest
import os
from consolemsg import error
from erppeek_wst import ClientWST
from yamlns import namespace as ns
from xmlrpc import client as xmlrpclib
from .claims import Claims
from .persons import persons

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
        self.maxDiff = None
        self.b2bdatapath = 'b2bdata'
        self.erp = None

        self.old_persons = None
        if hasattr(persons, 'path'):
            self.old_persons = getattr(persons, 'path')
        persons('testpersons.yaml')
        persons.path.write_text("""\
            erpusers:
              marc: Marc
        """, encoding='utf8')

        if not dbconfig:
            return
        if not dbconfig.erppeek:
            return
        self.erp = ClientWST(**dbconfig.erppeek)
        self.erp.begin()

    def tearDown(self):
        persons.path.unlink()
        persons(self.old_persons or False)
        try:
            self.erp and self.erp.rollback()
            self.erp and self.erp.close()
        except xmlrpclib.Fault as e:
            if 'transaction block' not in e.faultCode:
                raise

    from yamlns.testutils import assertNsEqual

    def crmCase(self, case_id, deep=False):
        """Retrieves checkeable erp fields for a CrmCase"""
        result = ns(self.erp.CrmCase.read(case_id, [
            'section_id',
            'name',
            'categ_id',
            'canal_id',
            'polissa_id',
            'partner_id',
            'partner_address_id',
            'state',
            'user_id',
        ]))

        fkname(result, "section_id")
        fkname(result, "categ_id")
        fkname(result, "canal_id")
        fkname(result, "partner_id")
        fkname(result, "partner_address_id")
        fkname(result, "polissa_id")
        fkname(result, "user_id")
        anonymize(result, 'partner_id')
        anonymize(result, 'partner_address_id')
        anonymize(result, 'user_id')

        if deep:
            result.atc_id = self.atcCase([
                ('crm_id', '=', case_id),
            ])
            if result.atc_id:
                del result.atc_id.id

        return result

    def atcCase(self, atc_case_id, deep=False):
        """Retrieves checkeable erp fields for an AtcCase"""
        result = self.erp.GiscedataAtc.read(atc_case_id, [
            'provincia',
            'total_cups',
            'cups_id',
            'subtipus_id',
            'reclamante',
            'resultat',
            'date',
            'email_from',
            'time_tracking_id',
            'state',
            'crm_id',
        ])
        if not result: return False
        result = ns(result[0])

        fkname(result, "cups_id")
        fkname(result, "subtipus_id")
        fkname(result, "time_tracking_id")
        fkname(result, "provincia")
        anonymize(result, "cups_id")
        anonymize(result, "email_from")

        crm_id = result.pop('crm_id')
        if deep:
            result.crm_id = crm_id and self.crmCase(crm_id[0])
            if crm_id:
                del result.crm_id.id

        return result

    def assertCrmCase(self, case_id, expected, deep=False):
        """Asserts that the CrmCase checkable erp fields do have
        the proper values"""
        if not expected:
            self.assertFalse(case_id)
            return
        self.assertTrue(case_id)
        result = self.crmCase(case_id, deep=deep)
        self.assertNsEqual(result, expected)

    def assertAtcCase(self, case_id, expected):
        """Asserts that the AtcCase checkable erp fields do have
        the proper values"""
        if not expected:
            self.assertFalse(case_id)
            return
        self.assertTrue(case_id)
        result = self.atcCase([case_id])
        self.assertNsEqual(result, expected)

    def claim_base(self, **kwds):
        """Provides a base for input atc cases to be feed"""
        base = ns.loads("""
            date: '2021-11-11T15:13:39.998Z'
            phone: '555444333'
            user: albert
            reason: '[RECLAMACIONS] 003. INCIDENCIA EN EQUIPOS DE MEDIDA'
            partner: S001975
            contract: '0013117'
            resolution: fair
            claimsection: RECLAMACIONS
            notes: User annotated text
        """)
        base.update(**kwds)
        return base

    def info_base(self, **kwds):
        base = ns.loads("""\
            date: '2021-11-11T15:13:39.998Z'
            phone: '555444333'
            user: albert
            reason: "[COBRAMENTS] Informació sobre el tall de subministrament"
            partner: S001975
            contract: '0013117'
            notes: User annotated text
        """)
        base.update(**kwds)
        return base


    def test_atcCategories(self):
        claims = Claims(self.erp)
        categories = claims.get_claims()
        self.assertB2BEqual(ns(categories=categories).dump())

    def test_crmCategories(self):
        claims = Claims(self.erp)
        categories = claims.crm_categories()
        self.assertB2BEqual(ns(categories=categories).dump())

    def test_categories(self):
        claims = Claims(self.erp)
        categories = claims.categories()
        self.assertB2BEqual(ns(categories=categories).dump())

    def test_createAtcCase_procedente(self):
        case = self.claim_base()

        claims = Claims(self.erp)
        case_id = claims.create_atc_case(case)
        self.assertAtcCase(case_id, """
            cups_id: ...M0F
            date: '2021-11-11 15:13:39.998'
            email_from: ...oop
            id: {}
            provincia: Barcelona
            reclamante: '01'
            resultat: '01'
            subtipus_id: '003'
            time_tracking_id: Comercialitzadora
            state: open
            total_cups: 1
        """.format(case_id))

    def test_createAtcCase_improcedente(self):
        case = self.claim_base(
            resolution='unfair',
        )

        claims = Claims(self.erp)
        case_id = claims.create_atc_case(case)
        self.assertAtcCase(case_id, """
            cups_id: ...M0F
            date: '2021-11-11 15:13:39.998'
            email_from: ...oop
            id: {}
            provincia: Barcelona
            reclamante: '01'
            resultat: '02' # <---------  THIS CHANGES
            subtipus_id: '003'
            time_tracking_id: Comercialitzadora
            state: open
            total_cups: 1
        """.format(case_id))

    def test_createAtcCase_noSolution(self):
        case = self.claim_base(
            resolution='irresolvable',
        )

        claims = Claims(self.erp)
        case_id = claims.create_atc_case(case)
        self.assertAtcCase(case_id, """
            cups_id: ...M0F
            date: '2021-11-11 15:13:39.998'
            email_from: ...oop
            id: {}
            provincia: Barcelona
            reclamante: '01'
            resultat: '03' # <---------  THIS CHANGES
            subtipus_id: '003'
            time_tracking_id: Comercialitzadora
            state: open
            total_cups: 1
        """.format(case_id))

    def test_createAtcCase_unsolved(self):
        case = self.claim_base(
            resolution='unsolved',
        )

        claims = Claims(self.erp)
        case_id = claims.create_atc_case(case)
        self.assertAtcCase(case_id, """
            cups_id: ...M0F
            date: '2021-11-11 15:13:39.998'
            email_from: ...oop
            id: {}
            provincia: Barcelona
            reclamante: '01'
            resultat: '' # <---------  THIS CHANGES
            subtipus_id: '003'
            time_tracking_id: Comercialitzadora
            state: open
            total_cups: 1
        """.format(case_id))

    def test_createCrmCase(self):
        case = self.info_base()
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            categ_id: '[COBRAMENTS] Informació sobre el tall de subministrament (com to'
            id: {}
            name: '[COBRAMENTS] Informació sobre el tall de subministrament'
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: '0013117'
            section_id: HelpDesk
            state: open
            user_id: false
        """.format(case_id))

    def test_createCrmCase_erpuserInPersons(self):
        case = self.claim_base(
            user='marc',
        )
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            categ_id: INCIDENCIA EN EQUIPOS DE MEDIDA
            id: {}
            name: INCIDENCIA EN EQUIPOS DE MEDIDA
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: '0013117'
            section_id: Atenció al Client / RECLAMACIONS
            state: open
            user_id: ...lló      # <--THIS CHANGES
        """.format(case_id))

    def test_createCrmCase_noContract(self):
        case = self.info_base(
            contract = '',
        )
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            categ_id: '[COBRAMENTS] Informació sobre el tall de subministrament (com to'
            id: {}
            name: '[COBRAMENTS] Informació sobre el tall de subministrament'
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: False # <---------  THIS CHANGES
            section_id: HelpDesk
            state: open
            user_id: false
        """.format(case_id))

    def test_createCrmCase_noPartner(self):
        case = self.info_base(
            contract = '',
            partner = '',
        )
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            id: {}
            canal_id: Teléfono
            categ_id: '[COBRAMENTS] Informació sobre el tall de subministrament (com to'
            name: '[COBRAMENTS] Informació sobre el tall de subministrament'
            partner_address_id: False
            partner_id: False # <---------  THIS CHANGES
            polissa_id: False # <---------  THIS CHANGES
            section_id: HelpDesk
            state: open
            user_id: false
        """.format(case_id))

    def test_createCrmCase_withClaim(self):
        case = self.claim_base() # <- This changes
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            categ_id: INCIDENCIA EN EQUIPOS DE MEDIDA  # <--- THIS CHANGES
            id: {}
            name: INCIDENCIA EN EQUIPOS DE MEDIDA  # <--- THIS CHANGES
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: '0013117'
            section_id: Atenció al Client / RECLAMACIONS  # <--- THIS CHANGES
            state: open
            user_id: false
        """.format(case_id))

    def test_createCrmCase_witBadReason(self):
        case = self.info_base(
            reason="Bad reason",
        )
        claims = Claims(self.erp)
        case_id = claims.create_crm_case(case)
        self.assertCrmCase(case_id, """\
            canal_id: Teléfono
            categ_id: False
            id: {}
            name: Bad reason
            partner_address_id: ...spí
            partner_id: ...osé
            polissa_id: '0013117'
            section_id: HelpDesk
            state: open
            user_id: false
        """.format(case_id))

    def test_createCase_withClaim_createsAtcAsWell(self):
        case = self.claim_base()
        claims = Claims(self.erp)
        case_id = claims.create_case(case)
        self.assertCrmCase(case_id, """\
            id: {}
            canal_id: Teléfono
            categ_id: INCIDENCIA EN EQUIPOS DE MEDIDA
            name: INCIDENCIA EN EQUIPOS DE MEDIDA
            partner_address_id: '...spí'
            partner_id: '...osé'
            polissa_id: '0013117'
            section_id: Atenció al Client / RECLAMACIONS
            state: open
            user_id: false
            atc_id:   # <----- THIS CHANGES
                cups_id: ...M0F
                date: '2021-11-11 15:13:39.998'
                email_from: ...oop
                provincia: Barcelona
                reclamante: '01'
                resultat: '01'
                subtipus_id: '003'
                time_tracking_id: Comercialitzadora
                state: open
                total_cups: 1
        """.format(case_id), deep=True)

    def test_createCase_withInfo_doesNotCreateAtc(self):
        case = self.info_base()
        claims = Claims(self.erp)
        case_id = claims.create_case(case)
        self.assertCrmCase(case_id, """\
            id: {}
            canal_id: Teléfono
            categ_id: '[COBRAMENTS] Informació sobre el tall de subministrament (com to'
            name: '[COBRAMENTS] Informació sobre el tall de subministrament'
            partner_address_id: '...spí'
            partner_id: '...osé'
            polissa_id: '0013117'
            section_id: HelpDesk
            state: open
            user_id: false
            atc_id: false   # <----- THIS CHANGES
        """.format(case_id), deep=True)


# vim: et ts=4 sw=4
