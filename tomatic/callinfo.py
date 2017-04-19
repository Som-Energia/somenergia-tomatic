# -*- coding: utf-8 -*-

import ooop
import dbconfig


class CallInfo(object):

    def __init__(self, O):
        self.O = O

    def searchAddresByPhone(self, phone):
        return self.O.ResPartnerAddress.search([('phone','=',phone)])

    def searchPartnerByAddressId(self, address_ids):
        partner_ids = []
        for address_id in address_ids:
            partner_address_register = self.O.ResPartnerAddress.read(address_id, ['id', 'partner_id'])
            if not partner_address_register or partner_address_register['partner_id'] == False: 
                continue
            partner_ids.append(partner_address_register['partner_id'][0])
        return partner_ids
    
    
# vim: ts=4 sw=4 et+