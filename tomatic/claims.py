# -*- encoding: utf-8 -*-
from yamlns import namespace as ns
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from .persons import persons
from consolemsg import warn

class Resolution(str, Enum):
    unsolved = 'unsolved'
    fair = 'fair'
    unfair = 'unfair'
    irresolvable = 'irresolvable'

class CallAnnotation(BaseModel):
    user: str
    date: str
    phone: str
    partner: str
    contract: str
    reason: str
    notes: str
    claimsection: Optional[str]
    resolution: Optional[Resolution]

def resolutionCode(case):
    return dict(
        unsolved = '',
        fair = '01',
        unfair = '02',
        irresolvable = '03',
    ).get(case.resolution, 'bad')


PHONE_CHANNEL = 2
TIME_TRACKER_COMERCIALIZADORA = 1
CLAIMANT = '01' # Titular de PS/ Usuario efectivo (Tabla 83)

# TODO: These two should be in the categories file, now hardcoded in ui code
CRM_CASE_SECTION_NAME = 'CONSULTA'
SECTION_TO_BE_SPECIFIED = 'ASSIGNAR USUARI'


def unknownState(erp):
    if hasattr(unknownState,'cached'):
        return unknownState.cached
    unknownState.cached = erp.ResCountryState.search([
        ('code', '=', '00')
    ])[0]
    return unknownState.cached


class Claims(object):

    def __init__(self, erp):
        self.erp = erp

    def _partnerId(self, partner_nif):
        if not partner_nif: return None
        partner = self.erp.ResPartner.search([
            ('ref', '=', partner_nif)
        ])
        return partner[0] if partner else None


    def _partnerAddress(self, partner_id):
        if not partner_id: return None
        return self.erp.read('res.partner.address',
            [('partner_id', '=', partner_id)],
            ['id', 'state_id', 'email']
        )[0]

    def _contractId(self, contract):
        if not contract: return None
        contract_id = self.erp.search('giscedata.polissa',[
            ("name", "=", contract)
        ])
        if contract_id: return contract_id[0]

    def _erpUser(self, person):
        # Try with explicit erpuser in persons.yaml
        erplogin = persons().get('erpusers',{}).get(person,None)
        if erplogin:
            user_ids = self.erp.search('res.users', [
                ('login', '=', erplogin)
            ])
            if user_ids: return user_ids[0]
        # if not found try with email
        email = persons().get('emails',{}).get(person,None)
        if email:
            address_ids = self.erp.search('res.partner.address', [
                ('email', '=', email),
            ])
            user_ids = self.erp.search('res.users', [
                ('address_id', 'in', address_ids),
            ])
            if user_ids: return user_ids[0]
        # No match found
        return None

    def _claimSubtypeByDescription(self, section_description):
        return self.erp.search('giscedata.subtipus.reclamacio', [
            ('desc', '=', section_description)
        ])[0]

    def _crmSectionID(self, section):
        return self.erp.search('crm.case.section', [
            ('name', 'ilike', section)
        ])[0]

    def _last_path(self, fullpath):
        return fullpath.split('/')[-1].strip()

    def categories(self):
        # TODO: Use a config file or a db backend
        keywords = ns.loads("""
            R002: protecció de dades
            R003: comptador
            R005: creuament comptadors
            R006: endarrerida
            R009: estimada
            R010: expedient
            R031: altres
            R057: expedient
            R101: compte bancari
            R102: duplicat
            R110: no entenen factures
            R111: no entenen contracte
            R114: encallada endarrerida
        """)

        ids = self.erp.search('crm.case.section', [])
        sections = [ ns(s) for s in self.erp.read('crm.case.section',  [
                ('code', 'ilike', 'ATC'),
                ('name', '!=', 'INFO'),
            ], [
                'name',
                'code',
                'parent_id',
            ]
        )]
        parentSections = { s.parent_id[0] for s in sections if s.parent_id }
        sections = [s for s in sections if s.id not in parentSections]

        ids = self.erp.search('crm.case.categ', [])
        categories = [
            ns(x) for x in self.erp.read('crm.case.categ', ids, [
                'name',
                'desc',
                'categ_code',
                'section_id',
            ]) or []
        ]
        return ns(
            categories=[
                ns(
                    name = cat.name,
                    code = cat.categ_code,
                    section = self._last_path(cat.section_id[1]) if cat.section_id else None,
                    isclaim = cat.categ_code and cat.categ_code[0] == 'R',
                    keywords = keywords.get(cat.categ_code,''),
                )
                for cat in sorted(categories, key=lambda x:x.categ_code or '')
                if cat.name[:1] == '['
                or (cat.categ_code and cat.categ_code[0] == 'R')
            ],
            sections=[
                dict(
                    code = s.code,
                    name = s.name,
                )
                for s in (ns(x) for x in sections)
            ],
        )

    def create_crm_case(self, case):
        CallAnnotation(**case)
        partner_id = self._partnerId(case.partner)
        partner_address = self._partnerAddress(partner_id)

        category_description = case.reason.split('.',1)[-1].strip()
        categ_ids = self.erp.search('crm.case.categ', [
            ('name', 'ilike', category_description),
        ])
        if not categ_ids:
            warn(f"Category not found {category_description}")
            categ_id = False
        else:
            categ_id = categ_ids[0]

        crm_section_id = self._crmSectionID(case.get('claimsection', 'HelpDesk'))

        data_crm = {
            'section_id': crm_section_id,
            'name': category_description,
            'canal_id': PHONE_CHANNEL,
            'categ_id': categ_id,
            'polissa_id': self._contractId(case.contract),
            'partner_id': partner_id,
            'partner_address_id': partner_address.get('id') if partner_address else False,
            'state': 'open', # TODO: 'done' if case.solved else 'open',
            'user_id': self._erpUser(case.user),
        }
        crm_id = self.erp.create('crm.case', data_crm)

        data_history = {
            'case_id': crm_id,
            'description': case.notes,
        }
        crm_history_id = self.erp.create('crm.case.history', data_history)

        return crm_id

    def create_atc_case(self, case):
        '''
        Expected case:
            date: D-M-YYYY H:M:S
            user: person
            reason: '[´section.name´] ´claim.name´. ´claim.desc´'
            partner: partner number
            contract: contract number
            # maybe unsolved, fair, unfair, irresolvable or null
            resolution: fair
            claimsection: section.name
            notes: comments
        '''
        CallAnnotation(**case)

        crm_case_id = self.create_crm_case(case)

        partner_id = self._partnerId(case.partner)
        partner_address = self._partnerAddress(partner_id)
        claim_subtype_id = self._claimSubtypeByDescription(
            case.reason.split('.',1)[-1].strip()
        )
        contract_id = self._contractId(case.contract)
        contract = self.erp.GiscedataPolissa.read(contract_id, ['cups'])
        state_id = partner_address.get('state_id')[0] if partner_address else unknownState(self.erp)
        data_atc = {
            'provincia': state_id,
            'total_cups': 1,
            'cups_id': contract['cups'][0] if contract else None,
            'subtipus_id': claim_subtype_id,
            'reclamante': CLAIMANT,
            'resultat': resolutionCode(case),
            'date': case.date,
            'email_from': partner_address.get('email') if partner_address else False,
            'time_tracking_id': TIME_TRACKER_COMERCIALIZADORA,
            'crm_id': crm_case_id,
        }
        case = self.erp.GiscedataAtc.create(data_atc)

        return case.id

    def is_atc_case(self, case):
        return case.get('claimsection', '') != ''

    def create_case(self, case):
        if not self.is_atc_case(case):
            return self.create_crm_case(case)
        # TODO: we had this, why asking again?
        atc_case_id = self.create_atc_case(case)
        atc_case = self.erp.GiscedataAtc.read(atc_case_id, ['crm_id'])
        return atc_case['crm_id'][0]


# vim: et ts=4 sw=4
