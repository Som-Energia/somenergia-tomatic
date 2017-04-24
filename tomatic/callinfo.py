# -*- coding: utf-8 -*-

import ooop
import dbconfig
from yamlns import namespace as ns 

class CallInfo(object):

    def __init__(self, O, anonymize=False):
        self.O = O
        self._anonymize = anonymize

    def anonymize(self, string):
        if not self._anonymize: return string
        return string[:2]+"..."+string[-2:]

    def addressByPhone(self, phone):
        return self.O.ResPartnerAddress.search([
            '|',
            ('phone','=',phone),
            ('mobile','=',phone),
            ])

    def searchPartnerByAddressId(self, address_ids):
        return [
            address['partner_id'][0]
            for address
            in self.O.ResPartnerAddress.read(address_ids, ['id', 'partner_id'])
            if address and address['partner_id']
            ]
    
    def getPartnerData(self, partner_id):
        partner_data = self.O.ResPartner.read(partner_id, [])
        partner_data = ns(partner_data[0])
        result = ns(partner=ns())
        result.partner.update(
            id_soci = partner_data.ref,
            lang = partner_data.lang,
            name = partner_data.name,
            city = partner_data.city,
            email = partner_data.www_email,
            polisses_ids = partner_data.polisses_ids,
            provincia = partner_data.www_provincia[1]['name'],
            )
        return result

    def getPartnersData(self, partners_ids):
        result = ns(partners = [])
        partners_data = self.O.ResPartner.read(partners_ids, [])
        for partner_data in partners_data:
            partner_data = ns(partner_data)
            partner_result = ns()
            partner_result.update(
                id_soci = partner_data.ref,
                lang = partner_data.lang,
                name = self.anonymize(partner_data.name),
                city = partner_data.city,
                email = self.anonymize(partner_data.www_email),
                provincia = partner_data.www_provincia[1]['name'],
                )
            partner_result.update(self.getPolisseData(partner_data.polisses_ids))            
            partner_block = ns()
            partner_block[self.anonymize(partner_data.name)] = partner_result
            result.partners.append(partner_block)
        return result

    def getPolisseData(self,polisses_ids):
        all_pol_data = self.O.GiscedataPolissa.read(polisses_ids,[
            'data_alta','data_baixa','potencia','cups','state','active','tarifa'
            ])        
        result = ns(polisses=[])
        for pol_data in all_pol_data:
            pol_data_ns = ns(polissa=ns())
            pol_data_ns.polissa.update(
                alta = pol_data['data_alta'],
                baixa = pol_data['data_baixa'] if pol_data['data_baixa'] else '',
                potencia = pol_data['potencia'],
                cups = pol_data['cups'][1],
                tarifa = pol_data['tarifa'][1],
                estat = pol_data['state'],
                )
            result.polisses.append(pol_data_ns)
        return result
    
    def getByPhone(self, phone):
        address_ids = self.addressByPhone(phone)
        partners_ids = self.searchPartnerByAddressId(address_ids)
        clean_partners_ids = sorted(list(set(partners_ids)))        
        result = ns()
        result.callid = phone
        result.update(self.getPartnersData(clean_partners_ids))
        return result

    
# vim: ts=4 sw=4 et
