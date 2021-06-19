module.exports = function() {

var m = require('mithril');

var Ripple = require('polythene-mithril-ripple').Ripple;
var Card = require('polythene-mithril-card').Card;
var Button = require('polythene-mithril-button').Button;
var Tabs = require('polythene-mithril-tabs').Tabs;

var CallInfo = require('./callinfo');
var ContractInfo = require('./contract');

var PartnerInfo = {};

var infoPartner = function(info){
  var aux = info.email.split(",");
  var emails = [];
  var url = "https://secure.helpscout.net/search/?query=";
  for(var i=0; i<aux.length; i++){
    emails.push(
      m(".partner-info-item",
        m("a", {"href":url+aux[i], target:"_blank", title: "Cerca al Helpscout"}, aux[i])
      )
    );
  }
  var dni = (info.dni.slice(0,2) === 'ES' ? info.dni.slice(2) : info.dni)
  return m(".partner-info",
    [
      m(".partner-info-item", [
        m("", m(".label-right",info.id_soci)),
        m("", m(".label",info.name))
      ]),
      m(".partner-info-item", dni),
      m(".partner-info-item", [info.city, ", ", info.state]),
      m(".partner-info-item", m("", emails)),
      m(".partner-info-item", (info.energetica ?
        m(".label-energetica","Soci d'Energetica.") : "")
      ),
      m(".partner-info-item", [
        m("", m(".label-right",info.lang)),
        m("", m(".label","Ha obert OV? "), (info.ov ? "Sí" : "No"))
      ]),
    ]
  );
}

function nameFromFullName(name) {
  var parts = name.split(',');
  if (!parts[1]){
    return name.split(' ')[0];
  }
  return  parts[1];
}

function buttons(partners) {
  return partners.map(
    (partner, index) => ({
      label: nameFromFullName(partner.name),
      selected: index == CallInfo.currentPerson,
    })
  );
}

var partnerCard = function(partners) {
  var partner = partners[CallInfo.currentPerson];
  return m(".partner-card", [
    m(".partner-tabs", [
      m(Tabs, {
        selected: "true",
        scrollable: "true",
        all: {
          activeSelected: "true",
          ink: "true",
        },
        tabs: buttons(partners),
        onChange: function(ev) {
          CallInfo.currentPerson = ev.index
          CallInfo.currentContract = 0
        }
      }),
    ]),
    m(Card, {
      className: 'card-info',
      content: [
        { text: {
          content: infoPartner(partner),
        }},
      ]
    })
  ]);
}


PartnerInfo.allInfo = function(info) {
  return m(
    ".main-info-card", [
      partnerCard(info.partners),
    ]
  );
}

return PartnerInfo;

}();
// vim: ts=2 sw=2 et
