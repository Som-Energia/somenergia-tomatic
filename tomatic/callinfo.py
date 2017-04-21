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
            lang = partner_data.lang,
            name = self.anonymize(partner_data.name),
            city = partner_data.city,
            email = self.anonymize(partner_data.www_email),
            polisses_ids = partner_data.polisses_ids,
            provincia = partner_data.www_provincia[1]['name'],
            )
        return result

    def getPartnersData2(self, partners_ids):
        result = ns(partners = [])
        for partner_id in partners_ids:
            partner_data = self.getPartnerData([partner_id])
            result.partners.append(partner_data)
        return result
    
    
    
    def getPartnersData(self, partners_ids):
        result = ns(partners = [])
        partners_data = self.O.ResPartner.read(partners_ids, [])
        for partner_data in partners_data:
            partner_data = ns(partner_data)
            partner_result = ns(partner=ns())
            partner_result.partner.update(
                lang = partner_data.lang,
                name = self.anonymize(partner_data.name),
                city = partner_data.city,
                email = self.anonymize(partner_data.www_email),
                polisses_ids = partner_data.polisses_ids,
                provincia = partner_data.www_provincia[1]['name'],
                )
            result.partners.append(partner_result)
        return result
        
        

    
    
    
    
    
    
    
    
    
    
    def getByPhone(self, phone):
        address_ids = self.addressByPhone(phone)
        partners_ids = self.searchPartnerByAddressId(address_ids)
        clean_partners_ids = sorted(list(set(partners_ids)))        
        result = ns()
        result.callid = phone
        result.partners = self.getPartnersData(clean_partners_ids)
        return result

    def getPolisseData(self,polisses_ids):
        polisse_data = self.O.GiscedataPolissa.read(155,['data_alta','potencia','cups'])
        print polisse_data
        result = ns(polisses=[])
        result.polisses.append(polisse_data)
        return result
         
# vim: ts=4 sw=4 et
