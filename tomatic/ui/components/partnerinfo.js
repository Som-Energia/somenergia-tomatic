module.exports = function() {

var m = require('mithril');

var Ripple = require('polythene-mithril-ripple').Ripple;
var Card = require('polythene-mithril-card').Card;
var Button = require('polythene-mithril-button').Button;
var Tabs = require('polythene-mithril-tabs').Tabs;

var CallInfo = require('./callinfo');

var PartnerInfo = {};

var infoPartner = function(){
  var partner = CallInfo.selectedPartner()
  var helpscouturl = "https://secure.helpscout.net/search/?query=";
  var emails = partner.email.split(",");
  var dni = (partner.dni.slice(0,2) === 'ES' ? partner.dni.slice(2) : partner.dni)
  return m(".partner-info",
    [
      m(".partner-info-item", [
        m("", m(".label-right",partner.id_soci)),
        m("", m(".label",partner.name))
      ]),
      m(".partner-info-item", dni),
      m(".partner-info-item", [partner.city, ", ", partner.state]),
      m(".partner-info-item", m("",
        emails.map(function(email) {
          return m(".partner-info-item",
            m("a", {
              href: helpscouturl+email,
              target:"_blank",
              title: "Cerca al Helpscout"
            }, email)
          );
        })
      )),
      m(".partner-info-item", (partner.energetica ?
        m(".label-energetica","Soci d'Energetica.") : "")
      ),
      m(".partner-info-item", [
        m("", m(".label-right",partner.lang)),
        m("", m(".label","Ha obert OV? "), (partner.ov ? "Sí" : "No"))
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
    function(partner, index) {
      return {
        label: nameFromFullName(partner.name),
        selected: index == CallInfo.currentPerson,
      };
    }
  );
}

var partnerCard = function(partners) {
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
          CallInfo.selectPartner(ev.index)
          if (ev.index) {
            CallInfo.notifyUsage('changePartner');
          }
        }
      }),
    ]),
    m(Card, {
      className: 'card-info',
      content: [
        { text: {
          content: infoPartner(),
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
