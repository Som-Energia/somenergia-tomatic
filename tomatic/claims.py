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
        return self.erp.ResPartnerAddress.read(
            [('partner_id', '=', partner_id)],
            ['id', 'state_id', 'email']
        )[0]

    def _contractId(self, contract):
        if not contract: return None
        contract_id = self.erp.GiscedataPolissa.search([("name", "=", contract)])
        if contract_id: return contract_id[0]

    def _erpUser(self, person):
        # Try with explicit erpuser in persons.yaml
        erplogin = persons().get('erpusers',{}).get(person,None)
        if erplogin:
            user_ids = self.erp.ResUsers.search([
                ('login', '=', erplogin)
            ])
            if user_ids: return user_ids[0]
        # if not found try with email
        email = persons().get('emails',{}).get(person,None)
        if email:
            address_ids = self.erp.ResPartnerAddress.search([
                ('email', '=', email),
            ])
            user_ids = self.erp.ResUsers.search([
                ('address_id', 'in', address_ids),
            ])
            if user_ids: return user_ids[0]
        # No match found
        return None

    def _claimSubtypeByDescription(self, section_description):
        claims_model = self.erp.GiscedataSubtipusReclamacio
        return claims_model.search([('desc', '=', section_description)])[0]

    def _crmSectionID(self, section):
        sections_model = self.erp.CrmCaseSection
        return sections_model.search([('name', 'ilike', section)])[0]

    def get_claims(self):
        claims_model = self.erp.GiscedataSubtipusReclamacio
        claims = []
        all_claim_ids = claims_model.search()

        for claim in claims_model.read(
            all_claim_ids,
            ['default_section', 'name', 'desc']
        ):
            claim_section = claim.get("default_section")

            section = (
                claim_section[1].split("/")[-1].strip()
                if claim_section else SECTION_TO_BE_SPECIFIED
            )

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
        partner_id = self._partnerId(case.partner)
        partner_address = self._partnerAddress(partner_id)

        category_description = case.reason.split('.',1)[-1].strip()
        categ_ids = self.erp.CrmCaseCateg.search([
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
            date: D-M-YYYY H:M:S
            user: person
            reason: '[´section.name´] ´claim.name´. ´claim.desc´'
            partner: partner number
            contract: contract number
            # maybe unsolved, fair, unfair, irresolvable or empty
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
