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

    def getByPhone(self, phone):
        return ns(partner=ns())
 
# vim: ts=4 sw=4 et
