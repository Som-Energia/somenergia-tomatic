# -*- coding: utf-8 -*-

import ooop
import dbconfig


class CallInfo(object):

    def __init__(self, O):
        self.O = O

    def searchAddresByPhone(self, phone):
        return self.O.ResPartnerAddress.search([('phone','=',phone)])

# vim: ts=4 sw=4 et+