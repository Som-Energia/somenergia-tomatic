# -*- encoding: utf-8 -*-
from yamlns import namespace as ns
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from .persons import persons

class Resolution(str, Enum):
    unsolved = 'unsolved'
    fair = 'fair'
    unfair = 'unfair'
    irresolvable = 'irresolvable'
    not_resolution = ''

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

PHONE_CHANNEL = 2
TIME_TRACKER_COMERCIALIZADORA = 1
CLAIMANT = '01' # Titular de PS/ Usuario efectivo (Tabla 83)
CRM_CASE_SECTION_NAME = 'CONSULTA'
DEFAULT_SECTION = 'ASSIGNAR USUARI'


def unknownState(erp):
    if hasattr(unknownState,'cached'):
        return unknownState.cached
    unknownState.cached = erp.ResCountryState.search([
        ('code', '=', '00')
    ])[0]
    return unknownState.cached

def partnerId(erp, partner_nif):
    if not partner_nif: return None
    partner = erp.ResPartner.search([
        ('ref', '=', partner_nif)
    ])
    return partner[0] if partner else None


def partnerAddress(erp, partner_id):
    if not partner_id: return None
    return erp.ResPartnerAddress.read(
        [('partner_id', '=', partner_id)],
        ['id', 'state_id', 'email']
    )[0]


def contractId(erp, contract):
    if not contract: return None
    contract_id = erp.GiscedataPolissa.search([("name", "=", contract)])
    if contract_id: return contract_id[0]

def erpUser(erp, person):
    # Try with explicit erpuser in persons.yaml
    erplogin = persons().get('erpusers',{}).get(person,None)
    if erplogin:
        user_ids = erp.ResUsers.search([
            ('login', '=', erplogin)
        ])
        if user_ids: return user_ids[0]
    # if not found try with email
    email = persons().get('emails',{}).get(person,None)
    if email:
        address_ids = erp.ResPartnerAddress.search([
            ('email', '=', email),
        ])
        user_ids = erp.ResUsers.search([
            ('address_id', 'in', address_ids),
        ])
        if user_ids: return user_ids[0]
    # No match found
    return None

def resolutionCode(case):
    return dict(
        unsolved = '',
        fair = '01',
        unfair = '02',
        irresolvable = '03',
    ).get(case.resolution, 'bad')

def sectionName(erp, section_id):
    claims_model = erp.GiscedataSubtipusReclamacio
    return claims_model.read(section_id, ['desc']).get('desc')


def claimSectionID(erp, section_description):
    claims_model = erp.GiscedataSubtipusReclamacio
    return claims_model.search([('desc', '=', section_description)])[0]


def crmSectionID(erp, section):
    sections_model = erp.CrmCaseSection
    return sections_model.search([('name', 'ilike', section)])[0]


class Claims(object):

    def __init__(self, erp):
        self.erp = erp

    def get_claims(self):
        claims_model = self.erp.GiscedataSubtipusReclamacio
        claims = []
        all_claim_ids = claims_model.search()

        for claim in claims_model.read(
            all_claim_ids,
            ['default_section', 'name', 'desc']
        ):
            claim_section = claim.get("default_section")

            section = DEFAULT_SECTION
            if claim_section:
                section = claim_section[1].split("/")[-1].strip()

            message = u"[{}] {}. {}".format(
                section,
                claim.get("name"),
                claim.get("desc")
            )
            claims.append(message)

        return claims

    def crm_categories(self):
        ids = self.erp.CrmCaseCateg.search([])
        return [
            f"[{CRM_CASE_SECTION_NAME}] {category['name']}"
            for category in self.erp.CrmCaseCateg.read(ids,['name'])
            if category['name'].startswith('[')
        ]


    def create_crm_case(self, case):
        CallAnnotation(**case)
        partner_id = partnerId(self.erp, case.partner)
        partner_address = partnerAddress(self.erp, partner_id)

        crm_section_id = crmSectionID(self.erp, case.claimsection)

        data_crm = {
            'section_id': crm_section_id,
            'name': case.reason.split('.',1)[-1].strip(),
            'canal_id': PHONE_CHANNEL,
            'polissa_id': contractId(self.erp, case.contract),
            'partner_id': partner_id,
            'partner_address_id': partner_address.get('id') if partner_address else False,
            'state': 'open', # TODO: 'done' if case.solved else 'open',
            'user_id': erpUser(self.erp, case.user),
        }
        crm_id = self.erp.CrmCase.create(data_crm).id

        data_history = {
            'case_id': crm_id,
            'description': case.notes,
        }
        crm_history_id = self.erp.CrmCaseHistory.create(data_history).id

        return crm_id

    def create_atc_case(self, case):
        '''
        Expected case:

        namespace(
            person:
              - date: D-M-YYYY H:M:S
                user: person
                reason: '[´section.name´] ´claim.name´. ´claim.desc´'
                partner: partner number
                contract: contract number
                # maybe unsolved, fair, unfair, irresolvable or empty
                resolution: fair
                claimsection: section.name
                notes: comments
                - ...
            ...
        )
        '''
        CallAnnotation(**case)

        crm_case_id = self.create_crm_case(case)

        partner_id = partnerId(self.erp, case.partner)
        partner_address = partnerAddress(self.erp, partner_id)
        claim_section_id = claimSectionID(
            self.erp, case.reason.split('.',1)[-1].strip()
        )
        contract_id = contractId(self.erp, case.contract)
        contract = self.erp.GiscedataPolissa.read(contract_id, ['cups'])
        state_id = partner_address.get('state_id')[0] if partner_address else unknownState(self.erp)
        data_atc = {
            'provincia': state_id,
            'total_cups': 1,
            'cups_id': contract['cups'][0] if contract else None,
            'subtipus_id': claim_section_id,
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


# vim: et ts=4 sw=4
