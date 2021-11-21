# -*- encoding: utf-8 -*-
from yamlns import namespace as ns

PHONE = 2
COMERCIALIZADORA = 1
RECLAMANTE = '01'


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

def resultat(case):
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

defaultSection = 'ASSIGNAR USUARI'

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

            section = defaultSection
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
            category['name']
            for category in self.erp.CrmCaseCateg.read(ids,['name'])
            if category['name'].startswith('[')
        ]


    def create_crm_case(self, case):
        ''
        partner_id = partnerId(self.erp, case.partner)
        partner_address = partnerAddress(self.erp, partner_id)
        crm_section_id = crmSectionID(self.erp, case.user)
        claim_section_id = claimSectionID(
            self.erp, case.reason.split('.')[-1].strip()
        )

        data_crm = {
            'section_id': crm_section_id,
            'name': sectionName(self.erp, claim_section_id),
            'canal_id': PHONE,
            'polissa_id': contractId(self.erp, case.contract),
            'partner_id': partner_id,
            'partner_address_id': partner_address.get('id') if partner_address else False,
            'state': 'open', # TODO: 'done' if case.solved else 'open',
            'user_id': '',
        }
        crm_id = self.erp.CrmCase.create(data_crm).id

        data_history = {
            'case_id': crm_id,
            'description': case.observations,
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
                user: section.name
                observations: comments
                # maybe unsolved, fair, unfair, irresolvable or empty
                resolution: fair
                - ...
            ...
        )
        '''
        partner_id = partnerId(self.erp, case.partner)
        partner_address = partnerAddress(self.erp, partner_id)
        claim_section_id = claimSectionID(
            self.erp, case.reason.split('.')[-1].strip()
        )
        crm_id = self.create_crm_case(case)
        contract_id = contractId(self.erp, case.contract)
        contract = self.erp.GiscedataPolissa.read(contract_id, ['cups'])

        data_atc = {
            'provincia': partner_address.get('state_id')[0] if partner_address else False,
            'total_cups': 1,
            'cups_id': contract['cups'][0] if contract else None,
            'subtipus_id': claim_section_id,
            'reclamante': RECLAMANTE,
            'resultat': resultat(case),
            'date': case.date,
            'email_from': partner_address.get('email') if partner_address else False,
            'time_tracking_id': COMERCIALIZADORA,
            'crm_id': crm_id,
        }
        #user_id = erpUser(self.erp, case.user)
        #if user_id:
        #    data_crm['create_uid'] = user_id
        case = self.erp.GiscedataAtc.create(data_atc)

        return case.id

# vim: et ts=4 sw=4
