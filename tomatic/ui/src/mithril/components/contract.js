var m = require('mithril')

var Spinner =
  require('polythene-mithril-material-design-spinner').MaterialDesignSpinner
var Ripple = require('polythene-mithril-ripple').Ripple
var Card = require('polythene-mithril-card').Card
var Button = require('polythene-mithril-button').Button
var IconButton = require('polythene-mithril-icon-button').IconButton
var Tabs = require('polythene-mithril-tabs').Tabs

var CallInfo = require('./callinfo')

var ContractInfo = {}

function formatContractNumber(number) {
  var result = number + ''
  while (result.length < 7) result = '0' + result
  return result
}

function formatInterval(contract) {
  var hasStart = contract.start_date !== false
  var hasEnd = contract.end_date != ''
  if (!hasStart) {
    return 'No especificat'
  }
  if (!hasEnd) {
    return contract.start_date + ' ⇨ Actualitat'
  }
  return contract.start_date + ' ⇨ ' + contract.end_date
}

var contractFields = function (contract, partner) {
  var s_num = formatContractNumber(contract.number)
  var from_til = formatInterval(contract)
  var roles = [
    ['T', contract.is_titular, 'Titular: Si té el contracte al seu nom'],
    [
      'A',
      contract.is_administrator,
      'Administradora: Si té permís de la titular per veure o gestionar-ho',
    ],
    ['S', contract.is_partner, 'Socia: Si és la socia vinculada al contracte'],
    [
      'P',
      contract.is_payer,
      "Pagadora: Si les factures s'emeten i cobren al seu nom (Rol a extingir)",
    ],
    ['N', contract.is_notifier, 'Notificada: Si en rep notificacions'],
  ]

  return m('.contract-info-box', [
    m('.contract-info-item', [
      m('', m('.label-right', from_til)),
      m('', m('.label', 'Número: '), s_num),
    ]),
    m(
      '.contract-info-item',
      m('.label', 'Nom del titular: '),
      contract.titular_name,
    ),
    contract.administrator
      ? m('.contract-info-item', [
          m('.label', 'Administradora: '),
          contract.administrator,
        ])
      : null,
    m('.contract-info-item', m('.label', 'CUPS: '), contract.cups),
    m(
      '.contract-info-item',
      m('.label', 'Adreça CUPS: '),
      contract.cups_adress,
    ),
    m('.contract-info-item', m('', m('.label', 'Tarifa: '), contract.fare)),
    m(
      '.contract-info-item',
      Object.keys(contract.power).map(function (key, index) {
        return m('', m('.label', key + ': '), contract.power[key] + ' kW')
      }),
    ),
    m('.contract-info-item', [m('.label', 'IBAN: '), contract.iban]),
    m('.contract-info-item', [
      m(
        '.label-right',
        'Rols: ',
        roles.map(function (rol) {
          var letter = rol[0]
          var active = rol[1]
          var title = rol[2]
          return m(
            '.contract-role' + (active ? '.active' : ''),
            { title: title },
            letter,
          )
        }),
      ),
    ]),
    m(
      '.contract-info-item',
      m('.label', 'Estat pendent: '),
      contract.pending_state != '' ? contract.pending_state : 'Esborrany',
    ),
    m('br'),
    extraInfo(contract),
  ])
}

ContractInfo.detailsPanel = function () {
  var contract = CallInfo.selectedContract()
  if (contract === null) {
    return null
  }
  var detailedViews = ['atr', 'invoices', 'readings']
  if (CallInfo.activeDetailedView === undefined) {
    CallInfo.activeDetailedView = 'atr'
  }
  var currentTab = CallInfo.activeDetailedView
  return m('.contract-details.flex', [
    m('.partner-card', [
      m('.partner-tabs', [
        m(Tabs, {
          selected: 'true',
          scrollable: 'true',
          all: {
            activeSelected: 'true',
            ink: 'true',
          },
          tabs: [
            {
              label: 'ATR',
              selected: currentTab == 'atr',
            },
            {
              label: 'Factures',
              selected: currentTab == 'invoices',
            },
            {
              label: 'Lectures',
              selected: currentTab == 'readings',
            },
          ],
          onChange: function (ev) {
            CallInfo.activeDetailedView = detailedViews[ev.index]
            if (ev.index) {
              CallInfo.notifyUsage('changeDetails')
            }
          },
        }),
      ]),
      m(Card, {
        className: 'card-info',
        content: [
          {
            text: {
              content: m('', [
                m('.contract-info-box', [
                  currentTab == 'atr' && [atrCases(contract.atr_cases)],
                  currentTab == 'invoices' && [lastInvoices(contract.invoices)],
                  currentTab == 'readings' && [
                    meterReadings(contract.lectures_comptadors),
                  ],
                ]),
              ]),
            },
          },
        ],
      }),
    ]),
  ])
}

var atrCases = function (cases) {
  if (cases === null) {
    return m(
      '.atr-cases',
      m('.loading.layout.vertical.center', [
        'Carregant casos ATR...',
        m(Spinner, { show: true }),
      ]),
    )
  }
  if (cases.length === 0) {
    return m(
      '.atr-cases',
      m('.loading.layout.vertical.center', ['No hi ha casos ATR disponibles.']),
    )
  }
  return m(
    '.atr-cases',
    m('table', [
      m('tr', [
        m('th', 'Data'),
        m('th', 'Procés'),
        m('th', 'Pas'),
        m('th', 'Estat'),
        m('th', 'Descripció'),
      ]),
      cases.map(function (atr_case) {
        return m('tr', [
          m('td', atr_case.date.slice(0, 10)), // Not the time
          m('td', atr_case.proces),
          m('td', atr_case.step),
          m(
            'td',
            m(atr_case.state != 'done' ? '.alert-case' : '', atr_case.state),
          ),
          m(
            'td',
            m(
              'span',
              { title: atr_case.additional_info },
              atr_case.additional_info,
            ),
          ),
        ])
      }),
    ]),
  )
}

var meterReadings = function (readings) {
  if (readings === null) {
    return m(
      '.meter-readings',
      m('.loading.layout.vertical.center', [
        'Carregant Lectures...',
        m(Spinner, { show: true }),
      ]),
    )
  }
  if (readings.length === 0) {
    return m(
      '.meter-readings',
      m('.loading.layout.vertical.center', ['No hi ha lectures disponibles.']),
    )
  }
  var meter_readings = []
  meter_readings.push(
    m('tr', [
      m('th', 'Comptador'),
      m('th', 'Data'),
      m('th', 'Lectura'),
      m('th', 'Origen'),
      m('th', 'Període'),
    ]),
  )
  for (const reading_index in readings) {
    const reading = readings[reading_index]
    meter_readings.push(
      m('tr', [
        m('td', reading.comptador),
        m('td', reading.data),
        m('td', reading.lectura),
        m('td', reading.origen),
        m('td', reading.periode),
      ]),
    )
  }
  return m('.meter-readings', m('table', meter_readings))
}

var lastInvoices = function (invoices) {
  if (invoices === null) {
    return m(
      '.factures',
      m('.loading.layout.vertical.center', [
        'Carregant Factures...',
        m(Spinner, { show: true }),
      ]),
    )
  }
  if (invoices.length === 0) {
    return m(
      '.factures',
      m('.loading.layout.vertical.center', ['No hi ha factures disponibles']),
    )
  }
  return m(
    '.factures',
    invoices.map(function (invoice) {
      return m('.factura-info-item', [
        m('div', [
          m('.label-right', invoice.initial_date, ' ⇨ ', invoice.final_date),
          m('', m('.label', 'Factura: '), invoice.number),
        ]),
        m('div', [m('.label', 'Empresa: '), invoice.payer]),
        m('table', [
          m('tr', [
            m('th', 'Total'),
            m('th', 'Energia'),
            m('th', 'Dies'),
            m('th', 'Emissió'),
            m('th', 'Venciment'),
            m('th', 'Estat'),
          ]),
          m('tr', [
            m('td', invoice.amount),
            m('td', invoice.energy_invoiced),
            m('td', invoice.days_invoiced),
            m('td', invoice.invoice_date),
            m('td', invoice.due_date),
            m('td', invoice.state),
          ]),
        ]),
      ])
    }),
  )
}

var extraInfo = function (contract) {
  var selfconsumption = contract.selfconsumption
  var generation = contract.generation
  var energetica = contract.energetica
  var suspended_invoicing = contract.suspended_invoicing
  var has_debt = contract.has_debt

  var info =
    !selfconsumption &&
    !generation &&
    !energetica &&
    !suspended_invoicing &&
    !has_debt
      ? m('no-info', 'No hi ha informació extra.')
      : m('.extra-info', [
          m(
            '',
            selfconsumption ? m('.label-selfconsumption', 'Autoconsum.') : '',
          ),
          m('', generation ? m('.label-generation', 'Rep Generation.') : ''),
          m('', energetica ? m('.label-energetica', "És d'EnergEtica.") : ''),
          m(
            '',
            suspended_invoicing ? m('.label-alert', 'Facturació suspesa.') : '',
          ),
          m('', has_debt ? m('.label-alert', 'Té deute: ' + has_debt) : ''),
        ])
  return m(Card, {
    className: 'extra-info',
    content: [
      {
        text: {
          content: info,
        },
      },
    ],
  })
}

var buttons = function (contracts) {
  var partner = CallInfo.selectedPartner()
  if (partner === null) {
    return null
  }
  return partner.contracts.map(function (contract, index) {
    return {
      label: m(
        'span' + (contract.end_date ? '.inactive-contract' : ''),
        contract.number,
      ),
      selected: index == CallInfo.currentContract,
    }
  })
}

var contractCard = function (partner) {
  var contract = CallInfo.selectedContract()
  return m('.partner-card', [
    m('.partner-tabs', [
      m(Tabs, {
        selected: 'true',
        scrollable: 'true',
        all: {
          activeSelected: 'true',
          ink: 'true',
        },
        tabs: buttons(),
        onChange: function (ev) {
          CallInfo.selectContract(ev.index)
          if (ev.index) {
            CallInfo.notifyUsage('changeContract')
          }
        },
      }),
    ]),
    m(Card, {
      className: 'card-info',
      content: [
        {
          text: {
            content: m('', [contractFields(contract, partner)]),
          },
        },
      ],
    }),
  ])
}

ContractInfo.mainPanel = function (info) {
  var partner = CallInfo.selectedPartner()
  if (
    partner === null ||
    partner.contracts === undefined ||
    partner.contracts.length === 0
  ) {
    return m('.contracts', [m('.no-info', 'No hi ha contractes.')])
  }
  return m('.contracts', contractCard(partner))
}

module.exports = ContractInfo
// vim: et sw=2 ts=2
