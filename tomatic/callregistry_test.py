# -*- encoding: utf-8 -*-

import unittest
import os
from consolemsg import error
from erppeek_wst import ClientWST
from yamlns import namespace as ns
from somutils.erptree import erptree
from xmlrpc import client as xmlrpclib
from .callregistry import CallRegistry
try:
    import dbconfig
except ImportError:
    dbconfig = None
"""
@unittest.skipIf(os.environ.get("TRAVIS"),
    "Database not available in Travis")
@unittest.skipIf(
    not dbconfig or not dbconfig.erppeek,
    "Requires configuring dbconfig.erppeek"
)"""

class CallRegistry_Test(unittest.TestCase):
    from yamlns.testutils import assertNsEqual

    def setUp(self):
        self.maxDiff=None
        if not dbconfig:
            return
        if not dbconfig.erppeek:
            return
        self.erp = ClientWST(**dbconfig.erppeek)
        self.erp.begin()

    def tearDown(self):
        try:
            self.erp.rollback()
        except xmlrpclib.Fault as e:
            if 'transaction block' not in e.faultCode:
                raise

    def test_annotateClaim(self):
        calls = CallRegistry(path='test', erp=self.erp)
        data = ns.loads("""\
            date: '2021-06-21T12:39:17Z'
            person: david
            reason: '[RECLAMACIONS] 002. PRIVACIDAD DE LOS DATOS'
            partner: T1001975
            contract: 0003684
            procedente: x
            improcedente: ''
            solved: x
            user: RECLAMACIONS
            cups: ES0031103223192001CA0F
            observations: Ho feu molt malament
        """)
        case_id = calls.annotateClaim(data)
        last_atc_case_id = self.erp.GiscedataAtc.search()[0]
        self.assertEqual(case_id, last_atc_case_id)
        case = self.getCase(case_id)
        self.assertNsEqual(case, f"""\
            active: true
            agent_actual: '06'
            business_days_with_same_agent: 0
            canal_id:
            - 2
            - Teléfono
            categ_id: false
            categ_ids: []
            crm_id:
              active: true
              canal_id:
              - 2
              - Teléfono
              categ_id: false
              categ_ids: []
              date: '2021-06-21 12:39:17'
              date_action_last: false
              date_action_next: false
              date_closed: false
              date_deadline: false
              description: false
              email_cc: false
              email_from: itc...oop
              email_last: Ho feu molt malament
              history_line:
              - {case.history_line[0].id}
              id: {case.crm_id.id}
              name: PRIVACIDAD DE LOS DATOS
              partner_address_id: Gar...spí
              partner_id: Gar...efa
              planned_cost: false
              planned_revenue: false
              polissa_id:
              - 3812
              - 0003684
              priority: '3'
              probability: false
              ref: false
              ref2: false
              section_id:
              - 24
              - Atenció al Client / RECLAMACIONS
              som: false
              state: done
              time_tracking_id:
              - 1
              - Comercialitzadora
              user_id: false
            cups_id: ES0031103223192001CA0F
            date: '2021-06-21 12:39:17'
            date_action_last: false
            date_action_next: false
            date_closed: false
            date_deadline: false
            description: false
            email_cc: false
            email_from: itc...oop
            email_last: Ho feu molt malament
            has_process: false
            history_line:
            - canal_id: false
              case_id:
              - {case.crm_id.id}
              - PRIVACIDAD DE LOS DATOS
              date: '{case.history_line[0].date}'
              description: Ho feu molt malament
              email: false
              id: {case.history_line[0].id}
              name: false
              note: '// ({case.history_line[0].date})
            
                Ho feu molt malament'
              section_id: false
              som: false
              time_spent: 0.0
              time_tracking_id: false
              user_id: false
            id: {case_id}
            name: PRIVACIDAD DE LOS DATOS
            not_allowed_subtipus: '[''036'', ''038'', ''039'', ''040'', ''041'', ''042'', ''043'',
              ''044'', ''045'', ''046'', ''048'', ''056'', ''066'', ''067'']'
            partner_address_id: Gar...spí
            partner_id: Gar...efa
            planned_cost: false
            planned_revenue: false
            polissa_id: 0003684
            priority: '3'
            probability: false
            process_step: ''
            provincia:
            - 9
            - Barcelona
            reclamante: '01'
            ref: false
            ref2: false
            resultat: '01'
            section_id:
            - 24
            - Atenció al Client / RECLAMACIONS
            sector: electric
            som: false
            state: done
            subtipus_desc: 002 - PRIVACIDAD DE LOS DATOS
            subtipus_id:
            - 2
            - '002'
            tancar_cac_al_finalitzar_r1: false
            time_tracking_id:
            - 1
            - Comercialitzadora
            total_cups: 1
            user_id: false
        """)


    def getCase(self, case_id):
        return erptree(case_id, self.erp.GiscedataAtc,
            expand = {
                'history_line': self.erp.CrmCaseHistory,
                'crm_id': self.erp.CrmCase,
            },
            pickName="""
                polissa_id
                cups_id
                partner_id
                partner_address_id
                crm_id.partner_id
                crm_id.partner_address_id
                """,
            anonymize="""
                partner_id
                partner_address_id
                email_from
                crm_id.email_from
                crm_id.partner_id
                crm_id.partner_address_id
                """,
            remove="""
                create_date
                create_uid
                log_ids
                history_line.log_id
                crm_id.create_date
                crm_id.create_uid
                crm_id.log_ids
                """,

        )





# vim: et ts=4 sw=4
