module.exports = function() {

var m = require('mithril');
var Ripple = require('polythene-mithril-ripple').Ripple;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var IconButton = require('polythene-mithril-icon-button').IconButton;
var Textfield = require('polythene-mithril-textfield').TextField;
var Card = require('polythene-mithril-card').Card;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var List = require ('polythene-mithril-list').List;
var Spinner = require('polythene-mithril-material-design-spinner').MaterialDesignSpinner;
var CallInfo = require('./callinfo');
var ContractInfo = require('./contract');
var PartnerInfo = require('./partnerinfo');
var Questionnaire = require('./questionnaire');

var CallInfoPage = {};

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

var searchIcon = function(){
  return m(".icon-search", [ m("i.fas.fa-search") ]);
}

var lockIcon = function(){
    return m(".icon-lock", [ m("i.fas.fa-lock-open") ]);
}

var lockedIcon = function(){
    return m(".icon-lock", [ m("i.fas.fa-lock") ]);
}

var newTabIcon = function(){
    return m(".icon-new-tab", [ m("i.fas.fa-external-link-alt") ]);
}

var refreshIcon = function(){
    return m(".icon-refresh", [ m("i.fas.fa-redo-alt") ]);
}

var settingsIcon = function() {
  return m(".icon-settings", [ m("i.fas.fa-cog") ]);
}

var typeOfSearch = function() {
  return m("select",
    {
      id: "search-by",
      className: ".select-search",
      onchange: function() {
        CallInfo.search_by = document.getElementById("search-by").value;
      },
    },
    [
      m("option", {"value":"phone"}, "Telèfon"),
      m("option", {"value":"name"}, "Cognoms/Nom"),
      m("option", {"value":"nif"}, "NIF"),
      m("option", {"value":"soci"}, "Número Soci"),
      m("option", {"value":"email"}, "Email"),
      m("option", {"value":"all"}, "Tot")
    ]
  );
}

var settingsDialog = function() {
  Dialog.show(function() { return {
    className: 'dialog-settings',
    title: 'Configuració:',
    backdrop: true,
    body: [
      m(Button, {
        className: 'btn-refresh',
        label: refreshIcon(),
        border: 'true',
        disabled: CallInfo.updatingClaims,
        events: {
          onclick: function() {
            updateClaims();
          },
        },
      }, m(Ripple)),
      CallInfo.updatingClaims ? [
        m("b", "Actualitzant reclamacions"),
        m("div", "Pot portar el seu temps, pots sortir mentrestant.")
      ] : m("b", "Actualitzar llistat de reclamacions")
    ],
    footerButtons: m(Button, {
      label: "Sortir",
      events: {
        onclick: function() {
          Dialog.hide({id:'settingsDialog'});
        },
      },
      raised: true,
    }),
  };}, {id:'settingsDialog'});
}


var customerSearch = function() {
  function keyEventHandler(event) {
    var char = event.which || event.keyCode;
    if (char === 13) {
      CallInfo.searchCustomer();
    }
  }
  return m('', {className:'busca-info'}, [
    m(".busca-info-title.layout.horizontal", [
      typeOfSearch(),
      m(Textfield, {
        className: 'txtf-phone flex',
        placeholder: "Cerca",
        onChange: function(state) {
          CallInfo.search = state.value;
        },
        events: {
          onkeypress: function(event){
            keyEventHandler(event)
          }
        },
        disabled: !CallInfo.refresh,
      }),
      m(IconButton, {
        className: 'btn-search',
        icon: searchIcon(),
        events: {
          onclick: function() {
            CallInfo.searchCustomer();
          },
        },
        disabled: !CallInfo.refresh,
      }),
    ]),
  ]);
}

var responsesMessage = function(info) {
  var time = (new Date(info.data)).toLocaleTimeString();
  return m('',
    m('span.time', time),
    ' ',
    m('span.phone', info.telefon ? info.telefon : "Cerca Manual"),
    m.trust('&nbsp;'),
    m.trust('&nbsp;'),
    info.motius?
      m('span.partner', {title: "Codi Titular"}, info.partner ? info.partner : "Sense informació") : '', 
    (info.motius && info.contracte)? [
      m.trust('&nbsp;'),
      m('span.contract', {title: "Codi Contracte"}, info.contracte)
    ]:'',
    !info.motius ? m('span.pending', " Pendent d'anotar"):'',
    ''
  );
}

var atencionsLog = function() {
  var aux = [];
  if (CallInfo.callLog.length === 0) {
    return m(".attended-calls-list", m(List, {
      compact: true,
      tiles: [
        m(ListTile, {
          className: "registres",
          compact: true,
          title: "Cap trucada al registre.",
        }),
      ],
    }));
  }
  var currentDate = new Date().toLocaleDateString();
  items = CallInfo.callLog.slice(0).reverse().map(function(item, index) {
    var itemClicked = function(ev) {
        if (item.motius !== "") return;
        if (CallInfo.call.date === item.data) {
          clearCallInfo();
          CallInfo.call.date = "";
        }
        else {
          CallInfo.call.date = item.data;
          CallInfo.refreshCall(item.telefon);
        }
    }
    var needsDate = false;
    var itemDate = new Date(item.data).toLocaleDateString();
    var itemWeekDay = new Date(item.data).toLocaleDateString(undefined, {weekday:'long'});
    if (itemDate !== currentDate) {
      currentDate = itemDate;
      needsDate = true;
    }
    var missatge = responsesMessage(item);
    var solved = item.motius !== "";
    return [
      needsDate? m(ListTile, {
        className:'registres dateseparator',
        title: itemWeekDay + " " + itemDate,
        header: true,
        disabled: true,
      }):'',
      m(ListTile, {
        className:
          CallInfo.call.date === item.data ?
          "registres selected" : "registres",
        selectable: true,
        hoverable: !solved,
        ink: !solved,
        title: missatge,
        subtitle: item.motius,
        selected: false,
        events: {
          onclick: itemClicked,
        },
        disabled: !CallInfo.refresh,
      })
    ];
  })
  return m(".attended-calls-list", m(List, {compact: true, tiles: items}));
}


var attendedCalls = function() {
  return m(Card, {
    className: 'card-attended-calls',
    content: [{
      primary: {
        title: m('.layout.horizontal', [
          m(".title", 'Trucades ateses'),
          m(".flex"), // expanding spacer
          m(IconButton, {
            className: 'btn-settings',
            icon: settingsIcon(),
            border: false,
            wash: true,
            compact: true,
            events: {
              onclick: function() {
                settingsDialog();
              },
            },
          }),
          m(IconButton, {
            className: 'btn-lock',
            icon: (CallInfo.refresh ? lockIcon() : lockedIcon()),
            border: false,
            wash: true,
            compact: true,
            title: CallInfo.refresh ? "Actualitza el cas automàticament":"Fixa el cas actual",
            events: {
              onclick: function() {
                CallInfo.refresh = !CallInfo.refresh
              },
            }
          }),
          m(IconButton, {
            className: "btn-new-tab",
            icon: newTabIcon(),
            border: false,
            wash: true,
            compact: true,
            title: "Obre una nova pestanya",
            url: {
              href: window.location,
              target:"_blank",
            }
          }),
        ])
      }},{
      text: {
        content: (CallInfo.callLog[0] === "lookingfor" ?
          m('center', m(Spinner, { show: "true" } )) : atencionsLog())
      }},
    ]
  });
}

CallInfoPage.view = function() {
  return m('.callinfo', [
    m(".all-info-call.layout.horizontal", [
      attendedCalls(),
      m(".layout.horizontal.flex", [
        m(".layout.vertical.flex", [
          customerSearch(),
          m('.plane-info',
            isEmpty(CallInfo.file_info)?
              m(".searching", 'No hi ha informació.',
                Questionnaire.annotationButton()
              ):(
            CallInfo.file_info[1] === "empty"?
              m(".searching", m(Spinner, { show: "true" } )):(
            CallInfo.file_info[1] === "toomuch"?
              m(".searching", 'Cerca poc específica, retorna masses resultats.',
                Questionnaire.annotationButton()
              ):(
              m('.plane-info', [
                  PartnerInfo.allInfo(CallInfo.file_info),
                  ContractInfo.view(
                    CallInfo.file_info,
                    CallInfo.currentPerson
                  ),
              ])
            ))),
          ),
        ])
      ])
    ])
  ]);
}


return CallInfoPage;

}();
// vim: ts=2 sw=2 et
