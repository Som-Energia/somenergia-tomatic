'use strict';

/// Cal Registry Form

module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var Ripple = require('polythene-mithril-ripple').Ripple;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var ButtonGroup = require('polythene-mithril-button-group').ButtonGroup;
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

var categoryFilter = "";
var isclaim = true;


var categoryList = function() {
  var categories = CallInfo.filteredCategories(categoryFilter, isclaim)

  return m(".motius", m(List, {
    compact: true,
    indentedBorder: true,
    compact: true,
    tiles: categories.map(function(category) {
      var displayText = category.isclaim? (
        "[" + (category.section || CallInfo.noSection) + "] " + category.name
      ):(
        category.name
      );
      return m(ListTile, {
        className: (
          CallInfo.call.category === category
          ? "llista-motius-selected"
          : "llista-motius-unselected"
        ),
        compact: true,
        selectable: true,
        ink: true,
        hover: true,
        title: displayText,
        selected: CallInfo.call.category === category,
        events: {
          onclick: function(ev) {
            CallInfo.call.category = category
          }
        },
        disabled: CallInfo.savingAnnotation,
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
  return m("",
    m(IconButton, {
      icon: clipboardIcon(),
      wash: true,
      compact: true,
      title: "Anota la trucada fent servir aquest contracte",
      events: {
        onclick: function() {
          Questionnaire.openCaseAnnotationDialog();
        },
      },
      disabled: (
        CallInfo.savingAnnotation ||
        Login.myName() === ""
      ),
    })
  );
}


Questionnaire.openCaseAnnotationDialog = function() {
  var partner = CallInfo.selectedPartner();
  var contract = CallInfo.selectedContract();
  if (CallInfo.call.date === "") {
    CallInfo.call.date = new Date().toISOString();
  }

  var sectionSelector = function() {
    var defaultSection = CallInfo.reasonTag(); // From the chosen category
    var sections = CallInfo.selectableSections();
    var selectable = defaultSection === CallInfo.noSection;
    return m("", [
      m("p", "Equip: " ),
      m("select",
        {
          id: "select-user",
          class: ".select-user",
          disabled: !selectable,
          default: defaultSection,
          oninput: function(ev) {
            CallInfo.annotation.tag = ev.target.value;
          },
        },
        m("option", {
          value: defaultSection,
          selected: !sections.includes(defaultSection)
        }, defaultSection),
        selectable && sections.map(function(option) {
          return m("option", {
              "value": option,
              "selected": CallInfo.annotation.tag === option
            }, option);
        })
      )
    ]);
  }

  var resolutionChoser = function() {
    return m(".case-resolution", [
      m("p", "Resolució:"),
      m(RadioGroup, {
        name: 'resolution',
        onChange: function(state) {
          CallInfo.annotation.resolution = state.value;
        },
        checkedValue: CallInfo.annotation.resolution,
        buttons: [{
            defaultChecked: true,
            label: "No resolt",
            value: 'unsolved',
        },{
            label: "Resolt; tenia raó",
            value: 'fair',
        },{
            label: "Resolt; no tenia raó",
            value: 'unfair',
        },{
            label: "Resolt; no es pot gestionar",
            value: 'irresolvable',
        }],
      }),
    ])
  }

  var buttons = function() {
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
            CallInfo.saveCallLog();
            Dialog.hide({ id: 'fillReclama' });
            Dialog.hide({ id: 'settingsDialog' });
          },
        },
        disabled: CallInfo.hasNoSection(),
        contained: true,
        raised: true,
      })
    ];
  }

  var emplenaReclamacio = function() {
    CallInfo.resetAnnotation();
    Dialog.show(function() {
      return {
        className: 'dialog-reclama',
        title: 'Reclamació:',
        backdrop: true,
        body: [
          sectionSelector(),
          m("br"),
          resolutionChoser(),
        ],
        footerButtons: buttons(),
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
          m(ButtonGroup,
            m(Button, {
              label: "Reclamació",
              extraWide: true,
              selected: isclaim,
              events: {
                onclick: function (ev) {
                  if (isclaim) return
                  isclaim = true;
                  CallInfo.call.category = "";
                }
              }
            }),
            m(Button, {
              label: "Consulta",
              extraWide: true,
              selected: !isclaim,
              events: {
                onclick: function (ev) {
                  if (!isclaim) return
                  isclaim = false;
                  CallInfo.call.category = "";
                  }
              }
            }),
          ),
          m(".reason-filter", [
            m(".motiu", 'Motiu: '),
            m(".filter",
              m(Textfield, {
                className: "textfield-filter",
                label: "Escriu per a filtrar",
                value: categoryFilter,
                dense: true,
                onChange: function(ev) {
                  categoryFilter = ev.value
                }
              })),
          ]),
          categoryList(),
          m(".final-motius", [
            m(Textfield, {
              className: "textfield-comentaris",
              label: "Comentaris",
              help: "Especifica més informació",
              multiLine: true,
              floatingLabel: true,
              rows: 5,
              dense: true,
              value: CallInfo.call.notes,
              onChange: function(params) {
                CallInfo.call.notes = params.value
              },
              disabled: CallInfo.savingAnnotation,
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
          label: CallInfo.savingAnnotation?"Desant":(
            isclaim?"Continua":"Desa"
          ),
          events: {
            onclick: function() {
              if (isclaim) {
                emplenaReclamacio();
              }
              else {
                CallInfo.saveCallLog();
                Dialog.hide({id:'settingsDialog'});
              }
            },
          },
          border: 'true',
          disabled: (
            CallInfo.savingAnnotation ||
            CallInfo.call.category === "" ||
            CallInfo.call.notes === "" ||
            Login.myName() === ""
          ),
        }, m(Ripple)),
      ]
    };},{id:'settingsDialog'});
}

return Questionnaire;

}();
// vim: ts=2 sw=2 et
