# -*- coding: utf-8 -*-

import ooop
import dbconfig
from yamlns import namespace as ns 

class CallInfo(object):

    def __init__(self, O, anonymize=False):
        self.O = O
        self._anonymize = anonymize
	self._partnerData = ns.loads("""partner: 
  lang:
  name:
  city:
  email:
  polisses_ids:
  provincia:
 """)

    def anonymize(self, string):
        if not self._anonymize: return string
        return string[:1]+"..."+string[-2:]

    def searchAddresByPhone(self, phone):
        return self.O.ResPartnerAddress.search([('phone','=',phone)])

    def searchAddresByMobile(self, phone):
        return self.O.ResPartnerAddress.search([('mobile','=',phone)])

    def searchPartnerByAddressId(self, address_ids):
        partner_ids = []
        for address_id in address_ids:
            partner_address_register = self.O.ResPartnerAddress.read(address_id, ['id', 'partner_id'])
            if not partner_address_register or partner_address_register['partner_id'] == False: 
                continue
            partner_ids.append(partner_address_register['partner_id'][0])
        return partner_ids
    
    def getPartnerData(self, partner_id):
	partner_data = self.O.ResPartner.read(partner_id, [])
	if not partner_data:
		return self._partnerData
	self._partnerData['partner']['lang'] = partner_data[0]['lang']
	self._partnerData['partner']['name'] = self.anonymize(partner_data[0]['name'])
	self._partnerData['partner']['city'] = partner_data[0]['city']
	self._partnerData['partner']['email'] = self.anonymize(partner_data[0]['www_email'])
        self._partnerData['partner']['polisses_ids'] = partner_data[0]['polisses_ids']
        self._partnerData['partner']['provincia'] = partner_data[0]['www_provincia'][1]['name']

	return self._partnerData

# vim: ts=4 sw=4 et
