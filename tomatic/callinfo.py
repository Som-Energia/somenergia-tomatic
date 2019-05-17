# -*- coding: utf-8 -*-

from yamlns import namespace as ns 

class CallInfo(object):

    def __init__(self, O, anonymize=False):
        self.O = O
        self._anonymize = anonymize

    def anonymize(self, string):
        if not self._anonymize: return string
        return "..."+string[-3:]

    def addressByPhone(self, phone):
        return self.O.ResPartnerAddress.search([
            '|',
            ('phone','=',phone),
            ('mobile','=',phone),
            ])

    def partnerByAddressId(self, address_ids):
        result = []
        if len(address_ids) == 0:
            return result
        return [
            address[0]
            for address 
            in self.O.ResPartnerAddress.read(address_ids,'partner_id')
            if address and address[0]
            ]

    def partnerInfo(self, partner_data):
        result = ns(
            id_soci = self.anonymize(partner_data.ref),
            lang = partner_data.lang,
            name = self.anonymize(partner_data.name),
            city = partner_data.city,
            email = self.anonymize(partner_data.www_email),
            contracts_ids = partner_data.polisses_ids,
            state = partner_data.www_provincia[1]['name'],
            )
        return result

    def getPartnerRelatedContracts(self,partner_id):
        contract_titular_ids = self.O.GiscedataPolissa.search([
            ('titular.id','=',partner_id),
            ])
        contract_pagador_ids = self.O.GiscedataPolissa.search([
            ('pagador.id','=',partner_id),
            ])
        contract_soci_ids = self.O.GiscedataPolissa.search([
            ('soci.id','=',partner_id),
            ])
        return sorted(list(set(contract_titular_ids + contract_pagador_ids + contract_soci_ids)))

    def partnersInfo(self, partners_ids):
        result = ns(partners = [])
        partners_data = self.O.ResPartner.read(partners_ids, [
            'city',
            'www_email',
            'www_provincia',
            'polisses_ids',
            'name',
            'ref',
            'lang',
        ])
        for partner_data in partners_data or []:
            partner_data = ns(partner_data)
            partner_result = self.partnerInfo(partner_data)
            contracts_ids = self.getPartnerRelatedContracts(partner_data.id)
            partner_result.update(self.contractInfo(contracts_ids,partner_data.id))
            del partner_result.contracts_ids
            result.partners.append(partner_result)
        return result

    def contractInfo(self, contracts_ids, partner_id):

        def hasOpenATR(contract_id, case):
            cases = self.O.GiscedataSwitching.search([
                ('cups_polissa_id', '=', contract_id),
                ('proces_id.name', '=', case),
                ('state', '!=', 'done')
            ])
            return len(cases) > 0

        if not contracts_ids:
            return ns(polisses=[])

        contracts = self.O.GiscedataPolissa.read(contracts_ids, [
            'data_alta',
            'data_baixa',
            'potencia',
            'cups',
            'state',
            'active',
            'tarifa',
            'name',
            'data_ultima_lectura',
            'facturacio_suspesa',
            'pending_state',
            'titular',
            'soci',
            'pagador',
        ])
        return ns(contracts=[
            ns(
                start_date = contract['data_alta'],
                end_date = contract['data_baixa'] if contract['data_baixa'] else '',
                power = contract['potencia'],
                cups = self.anonymize(contract['cups'][1]),
                fare = contract['tarifa'][1],
                state = contract['state'],
                number = contract['name'],
                last_invoiced = contract['data_ultima_lectura'],
                suspended_invoicing = contract['facturacio_suspesa'],
                pending_state = contract['pending_state'],
                has_open_r1s = hasOpenATR(contract['id'],'R1'),
                has_open_bs = hasOpenATR(contract['id'],'B1'),
                is_titular = contract['titular'][0] == partner_id,
                is_partner = contract['soci'][0] == partner_id,
                )
            for contract in contracts
            ])
    
    def getByPhone(self, phone):
        address_ids = self.addressByPhone(phone)
        partners_ids = self.partnerByAddressId(address_ids)
        clean_partners_ids = sorted(list(set(partners_ids)))        
        result = ns()
        result.callid = phone
        result.update(self.partnersInfo(clean_partners_ids))
        return result

    
# vim: ts=4 sw=4 et
