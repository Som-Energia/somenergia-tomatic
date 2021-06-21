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
  var last_invoiced = (contract.last_invoiced != "" ?
    contract.last_invoiced : "No especificada"
  );
  return m(".contract-info-box", [
    m(".contract-info-item", [
      m("", m(".label-right", from_til)),
      m("", m(".label","Número: "), s_num),
    ]),
    m(".contract-info-item",
      m('.label', "Nom del titular: "),
      contract.titular_name
    ),
    m(".contract-info-item", [
      m(".label-right", [
        Questionnaire.annotationButton(contract, partner),
      ]),
    m(".contract-info-item",
      m('.label', "CUPS: "),
      contract.cups
    ),
    m(".contract-info-item",
      m('.label', "Adreça CUPS: "),
      contract.cups_adress
    ),
    m(".contract-info-item",
      m("", m('.label', "Potència: "), contract.power),
    ),
    m(".contract-info-item",
      m("", m('.label', "Tarifa: "), contract.fare),
    ),
    m(".contract-info-item",
      m('.label', "Lot facturació: "),
      contract.lot_facturacio
    ),
    m(".contract-info-item",
      m('.label', "Data darrera lectura facturada: "),
      last_invoiced
    ),
      m('.label', "IBAN: "),
      contract.iban
    ]),
    m(
      ".contract-info-item",
      m('.label', "Estat pendent: "),
      (contract.pending_state != "" ? contract.pending_state : "No especificat")
    ),
    m(".contract-info-item", [
      m(".label-right", [
        (contract.is_titular ? m('span', {title: "Titular"}, "T ") : ""),
        (contract.is_partner ? m('span', {title: "Socia"}, "S ") : ""),
        (contract.is_payer ? m('span', {title: "Pagadora"}, "P ") : ""),
        (contract.is_notifier ? m('span', {title: "Rep les notificacions"}, "N ") : ""),
      ]),
      m(
        "",
        (contract.no_estimable ?
          m('.label', "No estimable.")
          : m('.label', "Estimable.")
        )
      ),
    ]),
  ]);
}

ContractInfo.extraView = function(info) {
  var partner = info.partners[CallInfo.currentPerson]
  if (
    partner === undefined ||
    partner.contracts === undefined ||
    partner.contracts.length === 0
  ) {
    return null;
  }
  var contract = partner.contracts[CallInfo.currentContract];
  return m(".contract-details.flex", [
    m(".partner-card", [
      m(Card, {
        className: 'card-info',
        content: [
          { text: {
            content: m("", [
              m(".contract-info-box", [
                extraInfo(
                  contract.generation, contract.energetica, contract.suspended_invoicing, contract.open_cases
                ),
                m('.card-part-header', "Darreres factures del contracte"),
                lastInvoices(contract.invoices),
                m('.card-part-header', "Darreres lectures del contracte"),
                meterReadings(contract.lectures_comptadors),
              ])
            ])
          }},
        ]
      }),
    ])
  ]);
}

var meterReadings = function(readings) {
  if (readings === null) {
    return m(".meter-readings", m(".loading.layout.vertical.center", [
      "Carregant Lectures...",
      m(Spinner, {show: true}),
    ]));
  }
  if (readings.length == 0) {
    return m(".contract-info-item", "No hi ha informació de comptadors.")
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
  generation, energetica, suspended_invoicing, open_cases
) {
  if (!generation && !energetica && !suspended_invoicing && open_cases.length == 0) {
    info = m("no-info", "No hi ha informació extra.")
  }
  else {
    info = m("", [
      m("",
        generation ? m(".label-generation","Rep Generation.") : ""
      ),
      m("",
        energetica ? m(".label-energetica","És d'EnergEtica.") : ""
      ),
      m("",
        (suspended_invoicing ? m(".label-alert","Facturació suspesa.") : "")
      ),
      m("",
        (open_cases.length > 0 ?
          m(".label-alert", ["Casos ATR oberts: ", open_cases])
          : ""
        )
      ),
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
  return contracts.map(function(contract, index) {
    return {
      label: contract.number,
      selected: index == CallInfo.currentContract,
    };
  });
}

var contractCard = function(partner) {
  var contract = partner.contracts[CallInfo.currentContract];
  return m(".partner-card", [
    m(".partner-tabs", [
      m(Tabs, {
        selected: "true",
        scrollable: "true",
        all: {
          activeSelected: "true",
          ink: "true",
        },
        tabs: buttons(partner.contracts),
        onChange: function(ev) {
          CallInfo.currentContract = ev.index
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


ContractInfo.view = function(info) {
  var partner = info.partners[CallInfo.currentPerson]
  if (partner.contracts == undefined) {
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
