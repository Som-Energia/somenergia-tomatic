# -*- coding: utf-8 -*-

from yamlns import namespace as ns
from enum import Enum, auto
from .config import params

ENERGETICA_PARTNER_ID = 38039


class AutoEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

class SearchField(AutoEnum):
    phone = auto()
    name = auto()
    nif = auto()
    soci = auto()
    email = auto()
    contract = auto()
    cups = auto()
    all = auto()

class CallInfo(object):

    def __init__(
        self, O, results_limit=None, anonymize=False, invoices_limit=None,
        meter_readings_limit=None
    ):
        self.O = O
        self.results_limit = results_limit
        self._anonymize = anonymize
        self.invoices_limit = invoices_limit
        self.meter_readings_limit = meter_readings_limit

        if not self.results_limit:
            self.results_limit = params().threshold_hits

        if not self.invoices_limit:
            self.invoices_limit = 12

        if not self.meter_readings_limit:
            self.meter_readings_limit = 12

    def anonymize(self, string):
        if not self._anonymize:
            return string
        if not string: return string
        return "..."+string[-3:]

    def addressByPhone(self, phone):
        return self.O.ResPartnerAddress.search([
            '|',
            ('phone', 'like', phone),
            ('mobile', 'like', phone),
            ])

    def addressByEmail(self, data):
        return self.O.ResPartnerAddress.search([
            ('email', 'ilike', data),
            ])

    def partnerBySoci(self, data):
        return self.O.ResPartner.search([
            ('ref', 'ilike', data),
            ])

    def partnerByDni(self, data):
        return self.O.ResPartner.search([
            ('vat', 'ilike', data),
            ])

    def partnerByName(self, data):
        return self.O.ResPartner.search([
            ('name', 'ilike', data),
            ])

    def partnerByAddressId(self, address_ids):
        address_ids = list(set(address_ids))
        if not address_ids: return []
        return [
            address[0]
            for address
            in self.O.ResPartnerAddress.read(address_ids, 'partner_id')
            if address and address[0]
            ]

    def partnerByContract(self, contract_number):
        contract_ids = self.O.GiscedataPolissa.search([
            ('name', '=', contract_number),
        ], 0,0,False, {'active_test': False})
        return self.partnersByContractIds(contract_ids)

    def partnerByCups(self, cups):
        contract_ids = self.O.GiscedataPolissa.search([
            ('cups.name', 'ilike', cups[:20]),
        ], 0,0,False, {'active_test': False})
        return self.partnersByContractIds(contract_ids)

    def partnersByContractIds(self, contract_ids):
        if not contract_ids: return []
        contracts = self.O.GiscedataPolissa.read(contract_ids, [
            'name',
            'titular',
            'pagador',
            'soci',
            'direccio_notificacio',
        ])
        result = set()
        for contract in contracts:
            contract = ns(contract)
            if contract.titular:
                result.add(contract.titular[0])
            if contract.pagador:
                result.add(contract.pagador[0])
            if contract.soci:
                result.add(contract.soci[0])
            if contract.direccio_notificacio:
                result.add(self.getPartnerId(contract.direccio_notificacio[0]))
        return list(result)

    def partnerInfo(self, partner_data):
        partner_category_id = self.O.IrModelData.get_object_reference(
            'som_partner_account','res_partner_category_soci')[1]

        result = ns(
            erp_id=partner_data.id,
            id_soci=self.anonymize(partner_data.ref) if partner_data.ref else "",
            lang=partner_data.lang,
            name=self.anonymize(partner_data.name),
            address=self.anonymize(partner_data.www_street) if partner_data.www_street else "",
            city=partner_data.www_municipi[1]['name'] if partner_data.www_municipi else "",
            email=self.anonymize(partner_data.www_email),
            postalcode=self.anonymize(partner_data.www_zip),
            state=partner_data.www_provincia[1]['name'] if partner_data.www_provincia else "",
            dni=self.anonymize(partner_data.vat),
            ov=partner_data.empowering_token != False,
            energetica=24 in partner_data.category_id,
            phones=(
                ([self.anonymize(partner_data.www_phone)] if partner_data.www_phone else [])+
                ([self.anonymize(partner_data.www_mobile)] if partner_data.www_mobile else [])
            ),
            comment=partner_data.comment or '',
            is_member=partner_category_id in partner_data.category_id,
        )
        return result

    def getPartnerRelatedContracts(self, partner_id):
        contract_ids = self.O.GiscedataPolissa.search([
            '|','|','|',
            ('titular', '=', partner_id),
            ('administradora', '=', partner_id),
            ('pagador', '=', partner_id),
            ('soci', '=', partner_id),
        ], 0, 0, False, {'active_test':False})
        if not contract_ids: return []
        contracts = self.O.GiscedataPolissa.read(contract_ids, [
            'titular',
            'administradora',
            'pagador',
            'soci',
            'active',
        ])
        # Sort contracts by activeness and relation to the partner
        return [
            contract['id']
            for contract in sorted(contracts,
                reverse=True,
                key=lambda x: (0
                    + (16 if x['active'] else 0)
                    + (8 if x['titular'][0] == partner_id else 0)
                    + (4 if x['administradora'] and x['administradora'][0]== partner_id else 0)
                    + (2 if x['pagador'][0] == partner_id else 0)
                    + (1 if x['soci'] and x['soci'][0] == partner_id else 0)
                )
            )
        ]

    def partnersInfo(self, partner_ids, shallow=False):
        no_partners = []
        result = ns(partners=[])
        partners_data = self.O.ResPartner.read(partner_ids, [
            'city',
            'www_email',
            'www_provincia',
            'www_municipi',
            'www_street',
            'www_zip',
            'www_phone',
            'www_mobile',
            'name',
            'ref',
            'lang',
            'vat',
            'empowering_token',
            'category_id',
            'comment',
        ])
        for partner_data in partners_data or []:
            partner_data = ns(partner_data)
            try:
                partner_result = self.partnerInfo(partner_data)
                contracts_ids = self.getPartnerRelatedContracts(
                    partner_data.id
                )
                partner_result.update(
                    self.contractInfo(contracts_ids, partner_data.id, shallow)
                )
                if partner_result.id_soci.startswith('S'):
                    result.partners.append(partner_result)
                else:
                    no_partners.append(partner_result)
            except Exception as e:
                print("Unexepected error found at partner id {}".format(
                    partner_data.id
                ))
                print(e)
                raise
        result.partners.extend(no_partners)
        return result

    def lastInvoices(self, contract_id):
        return self.lastInvoicesManyContracts([contract_id]).get(contract_id,[])

    def lastInvoicesManyContracts(self, contract_ids):
        def getInvoice(invoice_ids):
            return self.O.GiscedataFacturacioFactura.read(
                invoice_ids, [
                    'number',
                    'data_inici',
                    'data_final',
                    'partner_id',
                    'amount_total',
                    'energia_kwh',
                    'dies',
                    'date_invoice',
                    'date_due',
                    'state',
                    'polissa_id',
                ]
            ) or []

        result = { contract_id: [] for contract_id in contract_ids }

        last_invoices_ids = []
        for contract_id in contract_ids:
            invoice_ids = self.O.GiscedataFacturacioFactura.search([
                    ('polissa_id', '=', contract_id),
                    ('state', '!=', 'draft'),
                    ('type', 'in', ['out_invoice', 'out_refund'])
                ])
            last_invoices_ids.extend(invoice_ids)

        if not last_invoices_ids: return result

        for invoice in getInvoice(last_invoices_ids):
            contract_id = invoice['polissa_id'][0]
            data = dict(
                number=self.anonymize(invoice['number']),
                initial_date=invoice['data_inici'],
                final_date=invoice['data_final'],
                payer=self.anonymize(invoice['partner_id'][1]),
                amount=invoice['amount_total'],
                energy_invoiced=invoice['energia_kwh'] or 0,
                days_invoiced=invoice['dies'],
                invoice_date=invoice['date_invoice'],
                due_date=invoice['date_due'],
                state=invoice['state'],
            )
            result[contract_id].append(data)
        return result


    def meterReadings(self, contract_id):
        return self.meterReadingsManyContracts([contract_id])[contract_id]

    def meterReadingsManyContracts(self, contract_ids):
        result = { contract_id: [] for contract_id in contract_ids }

        meter_ids = self.O.GiscedataLecturesComptador.search([
            ('polissa', 'in', contract_ids),
            ('active', '=', True),
        ])
        if not meter_ids: return result

        meters = self.O.GiscedataLecturesComptador.read(
            meter_ids,
            ['lectures', 'name', 'polissa']
        )

        meter2contract = {
            meter['id']: meter['polissa'][0]
            for meter in meters
        }

        reading_ids = []
        for meter in meters:
            meter_readings = meter['lectures'] or []
            reading_ids.extend(meter_readings[:self.meter_readings_limit])
        if not reading_ids: return result

        readings = self.O.GiscedataLecturesLectura.read(
            reading_ids,
            ['name', 'lectura', 'origen_id', 'periode', 'comptador']
        )

        for reading in readings:
            contract_id = meter2contract[reading['comptador'][0]]
            data = dict(
                comptador=self.anonymize(reading['comptador'][1]),
                data=reading['name'],
                periode=reading['periode'][1],
                lectura=self.anonymize(str(reading['lectura'])),
                origen=reading['origen_id'][1],
            )
            result[contract_id].append(data)
        return result

    def atrCases(self, contract_id):
        return self.atrCasesManyContracts([contract_id])[contract_id]

    def atrCasesManyContracts(self, contract_ids):
        result = { contract_id: [] for contract_id in contract_ids }

        cases_ids = self.O.GiscedataSwitching.search([
            ('cups_polissa_id', 'in', contract_ids)
        ])

        if not cases_ids: return result

        cases = self.O.GiscedataSwitching.read(
            cases_ids,
            ['date', 'proces_id', 'step_id', 'state', 'additional_info', 'cups_polissa_id']
        )
        for case in cases:
            contract_id = case['cups_polissa_id'][0]
            data = dict(
                date=case.get('date'),
                proces=case.get('proces_id')[1],
                step=case.get('step_id')[1],
                state=case.get('state'),
                additional_info=case.get('additional_info')
            )
            result[contract_id].append(data)
        return result

    def getPartnerId(self, address_id):
        partner_ids = self.O.ResPartnerAddress.read(
            [address_id],
            ['partner_id']
        )
        if partner_ids and partner_ids[0]['partner_id']:
            return partner_ids[0]['partner_id'][0]
        return None


    def contractInfo(self, contracts_ids, partner_id, shallow=False):

        def getCUPSAdress(cups_id):
            cups_data = self.O.GiscedataCupsPs.read(
                cups_id, ['direccio', 'id_provincia']
            )
            return f"{cups_data['direccio']} {cups_data['id_provincia'][1]}"

        def hasGeneration(contract_id):
            assignations = self.O.GenerationkwhAssignment.search([
                ('contract_id', '=', contract_id),
                ('end_date', '=', None),
            ])
            return len(assignations) > 0

        def powers(powers):
            power_model = self.O.GiscedataPolissaPotenciaContractadaPeriode
            powers_dict = {
                f'P{i+1}': power_model.read(
                    power_id, ['potencia']
                ).get('potencia') for i, power_id in enumerate(powers)
            }
            return powers_dict

        if not contracts_ids:
            return ns(contracts=[])

        ret = ns(contracts=[])

        all_contracts = self.O.GiscedataPolissa.read(contracts_ids, [
            'data_alta',
            'data_baixa',
            'potencies_periode',
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
            'administradora',
            'administradora_permissions',
            'administradora_nif',
            'direccio_notificacio',
            'bank',
            'lot_facturacio',
            'no_estimable',
            'comptadors',
            'debt_amount',
            'autoconsumo',
        ])
        all_contracts_dict = {c['id']: c for c in all_contracts if c}
        for contract_id in contracts_ids:
            if contract_id not in all_contracts_dict:
                continue
            contract = all_contracts_dict[contract_id]
            def foreignName(c, atribute):
                if not c[atribute]: return ''
                return c[atribute][1]

            def foreignId(c, atribute):
                if not c[atribute]: return None
                return c[atribute][0]

            end_date = contract['data_baixa'] or ''
            is_titular = foreignId(contract,'titular') == partner_id
            is_partner = foreignId(contract,'soci') == partner_id
            is_administrator = foreignId(contract,'administradora') == partner_id
            notifier_address_id = foreignId(contract,'direccio_notificacio')
            is_notifier = self.getPartnerId(notifier_address_id) == partner_id
            is_payer = foreignId(contract,'pagador') == partner_id
            cups_adress = self.anonymize(
                getCUPSAdress(foreignId(contract,'cups'))
            )
            energetica = foreignId(contract, 'soci') == ENERGETICA_PARTNER_ID
            iban = self.anonymize(foreignName(contract,'bank'))
            lot_facturacio = foreignName(contract, 'lot_facturacio')
            lectures_comptadors = None if shallow else self.meterReadings(contract['id'])
            last_invoices = None if shallow else self.lastInvoices(contract['id'])
            partner_vat = self.O.ResPartner.read(
                foreignId(contract,'titular'), ['vat']
            ).get('vat')[2:]
            titular_name= self.anonymize(foreignName(contract,'titular'))
            if titular_name:
                titular_name += f" ({self.anonymize(partner_vat)})"
            administrator = foreignName(contract, 'administradora')
            if administrator:
                administrator += f" ({self.anonymize(contract.administradora_nif)})"
                permissions = dict(
                    manage = "Gestionar",
                    readonly = "Només consultar",
                ).get(contract['administradora_permissions'], "Error")
                administrator += f" [{permissions}]"

            debt = contract['debt_amount']
            atr_cases = None if shallow else self.atrCases(contract['id'])
            ret.contracts.append(
                ns(
                    erp_id=contract['id'],
                    start_date=contract['data_alta'],
                    end_date=end_date,
                    power=powers(contract['potencies_periode']),
                    cups=self.anonymize(foreignName(contract,'cups')),
                    fare=foreignName(contract,'tarifa'),
                    state=contract['state'],
                    number=contract['name'],
                    last_invoiced=contract['data_ultima_lectura'],
                    suspended_invoicing=contract['facturacio_suspesa'],
                    pending_state=contract['pending_state'],
                    is_titular=is_titular,
                    is_partner=is_partner,
                    is_notifier=is_notifier,
                    is_payer=is_payer,
                    is_administrator=is_administrator,
                    cups_adress=cups_adress,
                    titular_name= titular_name,
                    administrator = administrator,
                    energetica=energetica,
                    generation=hasGeneration(contract['id']),
                    iban=iban,
                    lot_facturacio=lot_facturacio,
                    no_estimable=contract['no_estimable'],
                    lectures_comptadors=lectures_comptadors,
                    invoices=last_invoices,
                    has_debt=debt if debt > 0.0 else False,
                    atr_cases=atr_cases,
                    selfconsumption=contract['autoconsumo'] not in [
                        '00',
                    ],
                )
            )
        return ret

    def getByPhone(self, phone, shallow=False):
        address_ids = self.addressByPhone(phone)
        partner_ids = self.partnerByAddressId(address_ids)
        return self.getByPartnersId(partner_ids, shallow)

    def getByEmail(self, email, shallow=False):
        email_ids = self.addressByEmail(email)
        partner_ids = self.partnerByAddressId(email_ids)
        return self.getByPartnersId(partner_ids, shallow)

    def getBySoci(self, soci, shallow=False):
        partner_ids = self.partnerBySoci(soci)
        return self.getByPartnersId(partner_ids, shallow)

    def getByDni(self, dni, shallow=False):
        partner_ids = self.partnerByDni(dni)
        return self.getByPartnersId(partner_ids, shallow)

    def getByName(self, name, shallow=False):
        partner_ids = self.partnerByName(name)
        return self.getByPartnersId(partner_ids, shallow)

    # TODO: Test
    def getByContract(self, number, shallow=False):
        partner_ids = self.partnerByContract(number)
        return self.getByPartnersId(partner_ids, shallow)

    # TODO: Test
    def getByCups(self, number, shallow=False):
        partner_ids = self.partnerByCups(number)
        return self.getByPartnersId(partner_ids, shallow)

    # TODO: Test
    def getByAny(self, data, shallow=False):
        address_ids = []
        address_ids += self.addressByEmail(data)
        address_ids += self.addressByPhone(data)
        partner_ids = []
        partner_ids += self.partnerByAddressId(address_ids)
        partner_ids += self.partnerByDni(data)
        partner_ids += self.partnerBySoci(data)
        partner_ids += self.partnerByName(data)
        partner_ids += self.partnerByContract(data)
        partner_ids += self.partnerByCups(data)
        return self.getByPartnersId(partner_ids, shallow)

    #TODO: untested
    def getByField(self, field: SearchField, data: str, shallow: bool=False):
        function = dict(
            phone = self.getByPhone,
            name = self.getByName,
            nif = self.getByDni,
            soci = self.getBySoci,
            email = self.getByEmail,
            contract = self.getByContract,
            cups = self.getByCups,
            all = self.getByAny,
        ).get(field)

        if function is None:
            return None

        return function(data, shallow)

    def getByPartnersId(self, partner_ids, shallow=False):
        if not partner_ids:
            return ns(partners=None)
        partner_ids = list(set(partner_ids))
        if self.results_limit and len(partner_ids) > self.results_limit:
            return ns(partners='Masses resultats')
        result = ns()
        result.update(self.partnersInfo(partner_ids, shallow))
        return result

    #TODO: untested
    def contractDetails(self, contract_numbers):
        contracts_ids = self.O.GiscedataPolissa.search([
            ('name', 'in', contract_numbers),
        ], 0,0,False, {'active_test': False})
        contracts = self.O.GiscedataPolissa.read(contracts_ids, [
            'name',
            'comptadors'
        ])

        if not contracts:
            return ns()

        invoicesByContract = self.lastInvoicesManyContracts(contracts_ids)
        atrCasesByContract = self.atrCasesManyContracts(contracts_ids)
        readingsByContract = self.meterReadingsManyContracts(contracts_ids)

        return ns(
            (contract['name'], ns(
                lectures_comptadors = readingsByContract.get(contract['id'],[]),
                invoices = invoicesByContract.get(contract['id'],[]),
                atr_cases = atrCasesByContract.get(contract['id'],[]),
            ))
            for contract in contracts
        )

# vim: ts=4 sw=4 et
