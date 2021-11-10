module.exports = function() {

var m = require('mithril');

var Spinner = require('polythene-mithril-material-design-spinner').MaterialDesignSpinner;
var Ripple = require('polythene-mithril-ripple').Ripple;
var Card = require('polythene-mithril-card').Card;
var Button = require('polythene-mithril-button').Button;
var IconButton = require('polythene-mithril-icon-button').IconButton;
var Tabs = require('polythene-mithril-tabs').Tabs;

var CallInfo = require('./callinfo');
var Questionnaire = require('./questionnaire');

var ContractInfo = {};

function formatContractNumber(number) {
  var result = number+"";
  while (result.length < 7) result = "0" + result;
  return result;
}

function formatInterval(contract) {
  var hasStart = contract.start_date !== false;
  var hasEnd = contract.end_date != "";
  if (!hasStart) {
    return "No especificat";
  }
  if (!hasEnd) {
    return contract.start_date + " ⇨ Actualitat";
  }
  return contract.start_date + " ⇨ " + contract.end_date;
}

var contractFields = function(contract, partner) {
  var s_num = formatContractNumber(contract.number);
  var from_til = formatInterval(contract);

  return m(".contract-info-box", [
    m(".contract-info-item", [
      m("", m(".label-right", from_til)),
      m("", m(".label","Número: "), s_num),
    ]),
    m(".contract-info-item",
      m('.label', "Nom del titular: "),
      contract.titular_name
    ),
    m(".contract-info-item",
      m('.label', "CUPS: "),
      contract.cups
    ),
    m(".contract-info-item",
      m('.label', "Adreça CUPS: "),
      contract.cups_adress
      ),
    m(".contract-info-item",
      m("", m('.label', "Tarifa: "), contract.fare)
    ),
    m(".contract-info-item",
      Object.keys(contract.power).map(function(key, index) {
        return m("", m(".label", key+": "), contract.power[key]+ ' kW');
      })
    ),
    m(".contract-info-item", [
      m('.label', "IBAN: "),
      contract.iban
    ]),
    m(".contract-info-item", [
      m(".label-right", [
        (contract.is_titular ? m('span', {title: "Titular"}, "T ") : ""),
        (contract.is_partner ? m('span', {title: "Socia"}, "S ") : ""),
        (contract.is_payer ? m('span', {title: "Pagadora"}, "P ") : ""),
        (contract.is_notifier ? m('span', {title: "Rep les notificacions"}, "N ") : ""),
      ]),
    ]),
    m(
      ".contract-info-item",
      m('.label', "Estat pendent: "),
      (contract.pending_state != "" ? contract.pending_state : "Esborrany")
    ),
    m("br"),
    extraInfo(
      contract.generation, contract.energetica,
      contract.suspended_invoicing, contract.has_debt
    ),
  ]);
}

ContractInfo.detailsPanel = function() {
  var contract = CallInfo.selectedContract();
  if (contract === null) { return null; }
  return m(".contract-details.flex", [
    m(".partner-card", [
      m(Card, {
        className: 'card-info',
        content: [
          { text: {
            content: m("", [
              m(".contract-info-box", [
                m('.card-part-header', "Darrers casos ATR"),
                atrCases(contract.atr_cases),
                m('.card-part-header', "Darreres factures del contracte"),
                lastInvoices(contract.invoices),
                m('.card-part-header', "Darreres lectures del contracte"),
                meterReadings(contract.lectures_comptadors),
              ])
            ])
          }},
        ],
      }),
    ])
  ]);
}


var atrCases = function(cases) {
  if (cases === null) {
    return m(".atr-cases", m(".loading.layout.vertical.center", [
      "Carregant casos ATR...",
      m(Spinner, {show: true}),
    ]));
  }
  if (cases.length === 0) {
    return m(".atr-cases", m(".loading.layout.vertical.center", [
      "No hi ha casos ATR disponibles.",
    ]));
  }
  return m(".atr-cases", m("table", [
    m("tr", [
      m("th", "Data"),
      m("th", "Procés"),
      m("th", "Pas"),
      m("th", "Estat"),
      m("th", "Descripció")
    ]),
    cases.map(function(atr_case) {
      return m("tr", [
        m("td", atr_case.date),
        m("td", atr_case.proces),
        m("td", atr_case.step),
        m("td", m(atr_case.state != 'done' ? ".alert-case" : "", atr_case.state)),
        m("td", m('span', {title: atr_case.additional_info}, atr_case.additional_info) )
      ]);
    })
  ]));
}


var meterReadings = function(readings) {
  if (readings === null) {
    return m(".meter-readings", m(".loading.layout.vertical.center", [
      "Carregant Lectures...",
      m(Spinner, {show: true}),
    ]));
  }
  if (readings.length === 0) {
    return m(".meter-readings", m(".loading.layout.vertical.center", [
      "No hi ha lectures disponibles.",
    ]));
  }
  meter_readings = [];
  meter_readings.push(
    m("tr", [
      m("th", "Comptador"),
      m("th", "Data"),
      m("th", "Lectura"),
      m("th", "Origen"),
      m("th", "Període")
    ])
  );
  for (reading_index in readings) {
    reading = readings[reading_index];
    meter_readings.push(
      m("tr", [
        m("td", reading.comptador),
        m("td", reading.data),
        m("td", reading.lectura),
        m("td", reading.origen),
        m("td", reading.periode)
      ])
    )
  }
  return m(".meter-readings", m("table", meter_readings));
}

var lastInvoices = function(invoices) {
  if (invoices === null) {
    return m(".factures",
      m(".factures-info",
        m(".loading.layout.vertical.center", [
          "Carregant Factures...",
          m(Spinner, {show: true}),
        ])
      )
    );
  }
  if (invoices.length === 0) {
    return m(".factures",
      m(".factures-info",
        m(".loading.layout.vertical.center", [
          "No hi ha factures disponibles"
        ])
      )
    );
  }
  return m(".factures", m(".factures-info", invoices.map(function(invoice) {
    return m(".factura-info-item", [
        m("div", [
          m(".label-right", invoice.initial_date, " ⇨ ", invoice.final_date),
          m("", m(".label", "Factura: "), invoice.number),
        ]),
        m("div", [m(".label", "Empresa: "), invoice.payer]),
        m("table", [
          m("tr", [
            m("th", "Total"),
            m("th", "Energia"),
            m("th", "Dies"),
            m("th", "Data"),
            m("th", "Venciment"),
            m("th", "Estat")
          ]),
          m("tr", [
            m("td", invoice.amount),
            m("td", invoice.energy_invoiced),
            m("td", invoice.days_invoiced),
            m("td", invoice.invoice_date),
            m("td", invoice.due_date),
            m("td", invoice.state),
          ])
        ])
      ]);
    })
  ));
}

var extraInfo = function(
  generation, energetica, suspended_invoicing, has_debt
) {
  if (!generation && !energetica && !suspended_invoicing && !has_debt) {
    info = m("no-info", "No hi ha informació extra.")
  }
  else {
    info = m(".extra-info", [
      m("",
        generation ? m(".label-generation","Rep Generation.") : ""
      ),
      m("",
        energetica ? m(".label-energetica","És d'EnergEtica.") : ""
      ),
      m("",
        suspended_invoicing ? m(".label-alert","Facturació suspesa.") : ""
      ),
      m("",
        has_debt ? m(".label-alert", "Té deute: " +has_debt) : ""
      )
    ])
  }
  return m(Card, {
    className: 'extra-info',
    content: [
      {
        text: {
          content: info
        }
      }
    ]
  })
}

var buttons = function(contracts) {
  var partner = CallInfo.selectedPartner()
  if (partner === null) { return null; }
  return partner.contracts.map(function(contract, index) {
    return {
      label: contract.number,
      selected: index == CallInfo.currentContract,
    };
  });
}

var contractCard = function(partner) {
  var contract = CallInfo.selectedContract()
  return m(".partner-card", [
    m(".partner-tabs", [
      m(Tabs, {
        selected: "true",
        scrollable: "true",
        all: {
          activeSelected: "true",
          ink: "true",
        },
        tabs: buttons(),
        onChange: function(ev) {
          CallInfo.selectContract(ev.index);
        }
      }),
    ]),
    m(Card, {
      className: 'card-info',
      content: [
        { text: {
          content: m("", [
            contractFields(contract, partner),
          ])
        }},
      ]
    }),
  ]);
}


ContractInfo.mainPanel = function(info) {
  var partner = CallInfo.selectedPartner();
  if (
    partner === null ||
    partner.contracts === undefined ||
    partner.contracts.length === 0
  ) {
    return m(".contracts", [m(".no-info", "No hi ha contractes.")]);
  }
  return m(
    ".contracts",
    contractCard(partner)
  );
}


return ContractInfo;

}();
// vim: et sw=2 ts=2
