'use strict';

module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var Ripple = require('polythene-mithril-ripple').Ripple;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var IconButton = require('polythene-mithril-icon-button').IconButton;
var Textfield = require('polythene-mithril-textfield').TextField;
var Card = require('polythene-mithril-card').Card;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var List = require ('polythene-mithril-list').List;
var Checkbox = require('polythene-mithril-checkbox').Checkbox;
var CallInfo = require('./callinfo');
var Login = require('./login');

var Questionnaire = {};

var call_reasons = CallInfo.call_reasons;
var reason_filter = "";


var getInfos = function() {
  m.request({
      method: 'GET',
      url: '/api/getInfos',
      extract: deyamlize,
  }).then(function(response){
      console.debug("Info GET Response: ",response);
      if (response.info.message !== "ok" ) {
          console.debug("Error al obtenir els infos: ", response.info.message)
      }
      else{
        call_reasons.infos = response.info.infos;
      }
  }, function(error) {
      console.debug('Info GET apicall failed: ', error);
  });
};
getInfos();


var postClaim = function(claim) {
  m.request({
    method: 'POST',
    url: '/api/atrCase',
    extract: deyamlize,
    body: claim
  }).then(function(response){
    console.debug("Info GET Response: ",response);
    if (response.info.message !== "ok" ) {
      console.debug("Error al fer el post del cas atr: ", response.info.message)
    }
    else{
      console.debug("ATC case saved")
      CallInfo.savingAnnotation = false;
    }
  }, function(error) {
    console.debug('Info GET apicall failed: ', error);
  });
};


var postAnnotation = function(annotation) {
  m.request({
    method: 'POST',
    url: '/api/infoCase',
    extract: deyamlize,
    body: annotation
  }).then(function(response){
    console.debug("Info POST Response: ",response);
    if (response.info.message !== "ok" ) {
      console.debug("Error al desar motius telefon: ", response.info.message)
    }
    else {
      console.debug("INFO case saved")
      CallInfo.savingAnnotation = false;
      CallInfo.call.extra = "";
      reason_filter = "";
      CallInfo.call.proc = false;
      CallInfo.call.improc = false;
    }
  }, function(error) {
    console.debug('Info POST apicall failed: ', error);
  });
}

var updateCall = function(date, partner_number, contract_number) {
    var info = {
        data: CallInfo.call.date,
        telefon: CallInfo.call.phone,
        partner: partner_number,
        contracte: contract_number,
        motius: CallInfo.call.reason,
    }
    m.request({
        method: 'POST',
        url: '/api/' + 'updatelog/'+ Login.getMyExt(),
        body: info,
        extract: deyamlize,
    }).then(function(response){
        console.debug("Info POST Response: ",response);
        if (response.info.message !== "ok") {
            console.debug("Error al fer log dels motius: ", response.info.message)
        }
        CallInfo.call.date = "";
    }, function(error) {
        console.debug('Info POST apicall failed: ', error);
    });
}

var saveLogCalls = function(phone, user, claim, contract, partner_code) {
  CallInfo.savingAnnotation = true;
  var contract_number = contract.number;
  var isodate = new Date(CallInfo.call.date).toISOString()
  updateCall(
    isodate,
    partner_code,
    contract.number
  );
  if (claim) {
    postClaim({
      "date": isodate,
      "person": user,
      "reason": CallInfo.call.reason,
      "partner": partner_code,
      "contract": contract.number,
      "procedente": (claim.proc ? "x" : ""),
      "improcedente": (claim.improc ? "x" : ""),
      "solved": (claim.solved ? "x" : ""),
      "user": (claim.tag ? claim.tag : "INFO"),
      "cups": contract.cups,
      "observations": CallInfo.call.extra,
    });
  }
  postAnnotation({
    "date": isodate,
    "phone": CallInfo.call.phone,
    "person": user,
    "reason": CallInfo.call.reason,
    "extra": CallInfo.call.extra,
  });
}


var llistaMotius = function( all = true ) {

  function contains(value) {
    var contains = value.toLowerCase().includes(reason_filter.toLowerCase());
    return contains;
  }

  var list_reasons = all ? [...call_reasons.infos, ...call_reasons.general] : call_reasons.infos;

  if (reason_filter !== "") {
    var filtered_regular = list_reasons.filter(contains);
    if (all) {
      var filtered_extras = call_reasons.extras.filter(contains);
      var extras = CallInfo.getExtras(filtered_extras);
      var filtered = filtered_regular.concat(extras);
    }
    else {
      var filtered = filtered_regular
    }
  }
  else {
    var filtered = list_reasons;
  }

  var disabled = (CallInfo.savingAnnotation || CallInfo.call.date === "" );

  return m(".motius", m(List, {
    compact: true,
    indentedBorder: true,
    tiles: filtered.map(function(reason) {
      return m(ListTile, {
        className: (
          CallInfo.call.reason === reason
          ? "llista-motius-selected"
          : "llista-motius-unselected"
        ),
        compact: true,
        selectable: true,
        ink: true,
        hover: true,
        title: reason,
        selected: CallInfo.call.reason == reason,
        events: {
          onclick: function(ev) {
            CallInfo.call.reason = reason
          }
        },
        disabled: disabled,
        bordered: true,
       });
    }),
  }));
}

var clipboardIcon = function(){
    return m(".icon-clipboard",
    [
        m("i.far.fa-clipboard"),
    ]);
}

Questionnaire.annotationButton = function(contract, partner_id) {
  return m("",
    m(IconButton, {
      icon: m("i.far.fa-clipboard.icon-clipboard"),
      icon: clipboardIcon(),
      wash: true,
      compact: true,
      title: "Anota la trucada fent servir aquest contracte",
      events: {
        onclick: function() {
          console.log("VEURE QÜESTIONARI INFOS")
          Questionnaire.openCaseAnnotationDialog(contract, partner_id);
        },
      },
      disabled: (
        CallInfo.savingAnnotation ||
        Login.myName() === ""
      ),
    }),
  );
}


Questionnaire.openCaseAnnotationDialog = function(contract, partner_id) {
  if (contract === undefined) {
    contract = {
      number: "",
      cumps: "",
    };
  }
  if (CallInfo.call.date === "") {
    CallInfo.call.date = new Date().toISOString();
  }

  var enviar = function(reclamacio = "") {
    saveLogCalls(
      CallInfo.call.phone,
      Login.myName(),
      reclamacio,
      contract,
      partner_id
    );
    CallInfo.call.reason = "";
  }

  var getTag = function(reason) {
    var matches = reason.match(/\[(.*?)\]/);
    if (matches) {
      return matches[1].trim();
    }
    return "";
  }

  var esReclamacio = function(type) {
    const info = "INFO";
    return (type != info);
  }

  var seleccionaUsuari = function(reclamacio, tag) {
    var section = tag;
    var options = [
      "RECLAMA",
      "FACTURA",
      "COBRAMENTS",
      "ATR A - COMER",
      "ATR B - COMER",
      "ATR C - COMER",
      "ATR M - COMER"
    ]
    return m("", [
      m("p", "Secció: " ),
      m("select",
        {
          id: "select-user",
          class: ".select-user",
          disabled: section !== "ASSIGNAR USUARI",
          default: section,
          onchange: function() {
            reclamacio.tag = document.getElementById("select-user").value;
          },
        },
        [
          m("option", {
            "value": options[0],
            "selected": section === options[0]
          }, options[0]),
          m("option", {
            "value": options[1],
            "selected": section === options[1]
          }, options[1]),
          m("option", {
            "value": options[2],
            "selected": section === options[2]
          }, options[2]),
          m("option", {
            "value": options[3],
            "selected": section === options[3]
          }, options[3]),
          m("option", {
            "value": options[4],
            "selected": section === options[4]
          }, options[4]),
          m("option", {
            "value": options[5],
            "selected": section === options[5]
          }, options[5]),
          m("option", {
            "value": options[6],
            "selected": section === options[6]
          }, options[6]),
          m("option", {
            "value": section,
            "selected": !options.includes(section)
          }, section)
        ]
      )
    ]);
  }

  var tipusATR = function(reclamacio) {
    return m("", [
      m("p", "Tipus: "),
      m(Checkbox, {
        className: "checkbox",
        name: 'proc',
        checked: reclamacio.proc,
        label: "Procedente",
        onChange: function() {
          reclamacio.proc = !CallInfo.call.proc;
          reclamacio.improc = false
        },
      }),
      m("br"),
      m(Checkbox, {
        className: "checkbox",
        name: 'improc',
        checked: reclamacio.improc,
        label: "Improcedente",
        onChange: function() {
          reclamacio.improc = !CallInfo.call.improc;
          reclamacio.proc = false
        },
      }),
      m("br"),
      m(Checkbox, {
        className: "checkbox",
        name: 'noproc',
        checked: (!reclamacio.improc && !reclamacio.proc),
        label: "No gestionable",
        onChange: function() {
          reclamacio.improc = false;
          reclamacio.proc = false;
        },
      }),
    ]);
  }

  var preguntarResolt = function(reclamacio) {
    return m("", [
      m("p", "S'ha resolt?"),
      m(Checkbox, {
        className: "checkbox",
        name: 'solved-yes',
        checked: reclamacio.solved,
        label: "Sí",
        onChange: function() {
            reclamacio.solved = !reclamacio.solved;
        },
      }),
      m("br"),
      m(Checkbox, {
        className: "checkbox",
        name: 'solved-no',
        checked: !reclamacio.solved,
        label: "No",
        onChange: function() {
            reclamacio.solved = !reclamacio.solved;
        },
      }),
    ]);
  }

  var buttons = function(reclamacio) {
    return [
      m(Button, {
        label: "Cancel·lar",
        events: {
          onclick: function() {
            Dialog.hide({id:'fillReclama'});
          },
        },
        raised: true,
      }),
      m(Button, {
        label: "Desa",
        events: {
          onclick: function() {
            enviar(reclamacio);
            Dialog.hide({ id: 'fillReclama' });
            Dialog.hide({ id: 'settingsDialog' });
          },
        },
        disabled: (reclamacio.tag === "ASSIGNAR USUARI"),
        contained: true,
        raised: true,
      })
    ];
  }

  var emplenaReclamacio = function(tag) {
    var reclamacio = {
      "proc": false,
      "improc": false,
      "solved": true,
      "tag": tag
    }
    Dialog.show(function() {
      return {
        className: 'dialog-reclama',
        title: 'Reclamació:',
        backdrop: true,
        body: [
          seleccionaUsuari(reclamacio, tag),
          m("br"),
          preguntarResolt(reclamacio),
          m("br"),
          (!reclamacio.solved && m("") || tipusATR(reclamacio)),
          m("br"),
        ],
        footerButtons: buttons(reclamacio),
      };},{id:'fillReclama'});
  }

  Dialog.show(function() {
    return {
      className: 'card-annotate-case',
      backdrop: true,
      title: "Anotar trucada",
      body: m(".layout.horizontal", [
        m(".layout.vertical.flex", [
          m(".final-motius", [
            m("strong", "Trucada:"),
            " ",
            CallInfo.call.phone || "Entrada manualment ",
            " a les "+new Date(CallInfo.call.date).toLocaleString(),
          ]),
          m(".final-motius", [
            m("strong", "De:"),
            " ",
            partner_id || "Cap persona especificada",
          ]),
          m(".final-motius", [
            m("strong", "Referent al contracte:"),
            " ",
            contract.number || " Cap contracte especificat",
          ]),
          m(".reason-filter", [
            m(".motiu", 'Motiu: '),
            m(".filter",
              m(Textfield, {
                className: "textfield-filter",
                label: "Escriure per filtrar",
                value: reason_filter,
                dense: true,
                onChange: function(params) {
                  reason_filter = params.value
                }
              })),
          ]),
          llistaMotius(!!partner_id ),
          m(".final-motius", [
            m("strong", "Comentaris:"),
            m(Textfield, {
              className: "textfield-comentaris",
              label: "Comentaris",
              help: "Especifica més informació",
              multiLine: true,
              floatingLabel: true,
              rows: 5,
              dense: true,
              value: CallInfo.call.extra,
              onChange: function(params) {
                CallInfo.call.extra = params.value
              },
              disabled: CallInfo.savingAnnotation || CallInfo.call.date === "",
            }),
          ]),
        ]),
      ]),
      footerButtons: [
        m(Button, {
          label: "Sortir",
          events: {
              onclick: function() {
                Dialog.hide({id:'settingsDialog'});
              },
          },
          raised: true,
        }),
        m(Button, {
          className: "save",
          label: CallInfo.savingAnnotation?"Desant":"Desa",
          events: {
            onclick: function() {
              var tag = getTag(CallInfo.call.reason);
              if (esReclamacio(tag)) {
                emplenaReclamacio(tag);
              }
              else {
                enviar();
                Dialog.hide({id:'settingsDialog'});
              }
            },
          },
          border: 'true',
          disabled: (
            CallInfo.savingAnnotation ||
            CallInfo.call.reason === "" ||
            CallInfo.call.extra === "" ||
            CallInfo.call.date === "" ||
            Login.myName() === ""
          ),
        }, m(Ripple)),
      ]
    };},{id:'settingsDialog'});
}

return Questionnaire;

}();
// vim: ts=2 sw=2 et
