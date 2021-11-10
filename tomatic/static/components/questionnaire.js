'use strict';

/// Cal Registry Form

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
var RadioGroup = require('polythene-mithril-radio-group').RadioGroup;
var RadioButton = require('polythene-mithril-radio-button').RadioButton;
var CallInfo = require('./callinfo');
var Login = require('./login');

var Questionnaire = {};

var call_reasons = CallInfo.call_reasons;
var reason_filter = "";


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

var updateCall = function(data) {
    m.request({
        method: 'POST',
        url: '/api/updatelog/'+ Login.myName(),
        body: data,
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

var saveLogCalls = function(phone, user, claim, contract, partner) {
  CallInfo.savingAnnotation = true;
  var partner_code = partner!==null ? partner.id_soci : "";
  var contract_number = contract!==null ? contract.number : "";
  var contract_cups = contract!==null ? contract.cups : "";
  var isodate = CallInfo.call.date || new Date().toISOString()
  updateCall({
    "data": isodate,
    "telefon": CallInfo.call.phone,
    "partner": partner_code,
    "contracte": contract_number,
    "motius": CallInfo.call.reason,
  })
  if (claim) {
    postClaim({
      "date": isodate,
      "person": user,
      "reason": CallInfo.call.reason,
      "partner": partner_code,
      "contract": contract_number,
      "procedente": (claim.proc ? "x" : ""),
      "improcedente": (claim.improc ? "x" : ""),
      "solved": (claim.solved ? "x" : ""),
      "user": (claim.tag ? claim.tag : "INFO"),
      "cups": contract_cups,
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


var llistaMotius = function() {
  const all=true;
  function contains(value) {
    var contains = value.toLowerCase().includes(reason_filter.toLowerCase());
    return contains;
  }
  var list_reasons = [].concat(
    call_reasons.infos,
    all ? call_reasons.general : []
  );

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

Questionnaire.annotationButton = function() {
  var partner = CallInfo.selectedPartner();
  var contract = CallInfo.selectedContract();
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
          Questionnaire.openCaseAnnotationDialog(contract, partner);
        },
      },
      disabled: (
        CallInfo.savingAnnotation ||
        Login.myName() === ""
      ),
    })
  );
}


Questionnaire.openCaseAnnotationDialog = function(contract, partner) {
  if (CallInfo.call.date === "") {
    CallInfo.call.date = new Date().toISOString();
  }

  var enviar = function(reclamacio) {
    saveLogCalls(
      CallInfo.call.phone,
      Login.myName(),
      reclamacio,
      contract,
      partner
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
      m("p", "Equip: " ),
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
        options.map(function(option) {
          return
            m("option", {
              "value": option,
              "selected": section === option
            }, option);
        }),
        m("option", {
          "value": section,
          "selected": !options.includes(section)
        }, section)
      )
    ]);
  }

  var preguntarResolt = function(reclamacio) {
    return m(".case-resolution", [
      m("p", "Resolució:"),
      m(RadioGroup, {
        name: 'resolution',
        onChange: function(state) {
          reclamacio.solved = state.value != 'unsolved';
          reclamacio.proc = state.value == 'procedent';
          reclamacio.improc = state.value == 'improcedent';
        },
        checkedValue: (
          !reclamacio.solved ? 'unsolved' :
          reclamacio.proc ? 'procedent' :
          reclamacio.improc ? 'improcedent' :
          'nogestionable'
        ),
        buttons: [{
            defaultChecked: true,
            label: "No resolt",
            value: 'unsolved',
        },{
            label: "Resolt; tenia raó",
            value: 'procedent',
        },{
            label: "Resolt; no tenia raó",
            value: 'improcedent',
        },{
            label: "Resolt; no es podia fer res",
            value: 'nogestionable',
        }],
      }),
    ])
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
      "solved": false,
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
            m('strong', " el dia "), 
            new Date(CallInfo.call.date).toLocaleDateString(),
            m('strong', " a les "),
            new Date(CallInfo.call.date).toLocaleTimeString(),
          ]),
          m(".final-motius", [
            m("strong", "De:"),
            " ",
            partner !== null ? [
              partner.id_soci,
              partner.dni.replace("ES",""),
              partner.name,
              ].join(" - ")
            : "Cap persona especificada",
          ]),
          m(".final-motius", [
            m("strong", "Referent al contracte:"),
            " ",
            contract !== null? (
              contract.number + " - " + contract.cups_adress
            ): " Cap contracte especificat",
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
          llistaMotius(),
          m(".final-motius", [
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
                enviar("");
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
