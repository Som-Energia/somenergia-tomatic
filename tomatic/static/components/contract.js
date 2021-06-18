module.exports = function() {

var m = require('mithril');

var Ripple = require('polythene-mithril-ripple').Ripple;
var Card = require('polythene-mithril-card').Card;
var Button = require('polythene-mithril-button').Button;
var IconButton = require('polythene-mithril-icon-button').IconButton;
var Tabs = require('polythene-mithril-tabs').Tabs;

var Questionnaire = require('./questionnaire');

var ContractInfo = {};
ContractInfo.main_contract = 0;

function formatContractNumber(number) {
  var result = number+"";
  while (result.length < 7) result = "0" + result;
}

var contractCard = function(contract, partner_id) {
  var s_num = formatContractNumber(contract.number)
  var from_til = (contract.start_date !== false ?
    contract.start_date : "No especificat"
  );
  var aux = contract.end_date;
  var last_invoiced = (contract.last_invoiced != "" ?
    contract.last_invoiced : "No especificada"
  );
  if (aux == "" && from_til !== "No especificat") {
    from_til += " ⇨ Actualitat"
  }
  else if (from_til !== "No especificat") {
    from_til += (" ⇨ " + aux);
  }
  return m(".contract-info-box", [
    m(".contract-info-item", [
      m("", m(".label-right", from_til)),
      m("", m(".label","Número: "), s_num),
    ]),
    m(".contract-info-item",
      m('.label', "Nom del titular: "),
      info.titular_name
    ),
    m(".contract-info-item", [
      m(".label-right", [
        Questionnaire.annotationButton(
            {
              'cups': contract.cups,
              'number': s_num 
            },
            partner_id
        ),
      ]),
    m(".contract-info-item",
      m('.label', "CUPS: "),
      info.cups
    ),
    m(".contract-info-item",
      m('.label', "Adreça CUPS: "),
      info.cups_adress
    ),
    m(".contract-info-item",
      m("", m('.label', "Potència: "), info.power),
    ),
    m(".contract-info-item",
      m("", m('.label', "Tarifa: "), info.fare),
    ),
    m(".contract-info-item",
      m('.label', "Lot facturació: "),
      info.lot_facturacio
    ),
    m(".contract-info-item",
      m('.label', "Data última lectura facturada: "),
      last_invoiced
    ),
      m('.label', "IBAN: "),
      info.iban
    ]),
    m(
      ".contract-info-item",
      m('.label', "Estat pendent: "),
      (info.pending_state != "" ? info.pending_state : "No especificat")
    ),
    m(".contract-info-item", [
      m(".label-right", [
        (info.is_titular ? m('span', {title: "Titular"}, "T ") : ""),
        (info.is_partner ? m('span', {title: "Socia"}, "S ") : ""),
        (info.is_payer ? m('span', {title: "Pagadora"}, "P ") : ""),
        (info.is_notifier ? m('span', {title: "Rep les notificacions"}, "N ") : ""),
      ]),
      m(
        "",
        (info.no_estimable ?
          m('.label', "No estimable.")
          : m('.label', "Estimable.")
        )
      ),
    ]),
    extraInfo(
      info.generation, info.energetica, info.suspended_invoicing, info.open_cases
    ),
    meterReadings(info.lectures_comptadors),
    lastInvoices(info.invoices),
  ]);
}

var meterReadings = function(readings) {
  if (readings === null) {
    return m(".meter-readings", m("table", 
      m('tr', m('td', "Carregant Lectures..."))
    ));
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
        m(".factura-info-item", "Carregant Factures...")
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
        generation ? m(".label-generation","Té Generation.") : ""
      ),
      m("",
        energetica ? m(".label-energetica","És Energetica.") : ""
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
    var contract = 0;
    var numOfContracts = contracts.length;
    var aux = [];
    for (contract; contract < numOfContracts; contract++) {
        aux[contract] = {label: contracts[contract].number};
    }

    return aux;
}

var specificContractCard = function(contract, button, partner_id) {
  return m(".partner-card", [
    m(".partner-tabs", [
      m(Tabs, {
        selected: "true",
        scrollable: "true",
        all: {
          activeSelected: "true",
          ink: "true",
        },
        tabs: button,
        onChange: function(ev) {
          ContractInfo.main_contract = ev.index
        }
      }),
    ]),
    m(Card, {
      className: 'card-info',
      content: [
        { text: {
          content: m("", [
            contractCard(contract, partner_id),
          ])
        }},
      ]
    }),
  ]);
}

ContractInfo.view = function(info, main_partner) {
  if (info.partners[main_partner].contracts == undefined) {
    return m(".contracts", [m(".no-info", "No hi ha contractes.")]);
  }
  var contracts = info.partners[main_partner].contracts;
  return m(
    ".contracts",
    specificContractCard(
      contracts[ContractInfo.main_contract],
      buttons(info.partners[main_partner].contracts),
      info.partners[main_partner].id_soci
    )
  );
}


return ContractInfo;

}();
// vim: et sw=2 ts=2
