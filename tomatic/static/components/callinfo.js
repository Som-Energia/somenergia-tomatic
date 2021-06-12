module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var Ripple = require('polythene-mithril-ripple').Ripple;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var Textfield = require('polythene-mithril-textfield').TextField;
var Card = require('polythene-mithril-card').Card;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var List = require ('polythene-mithril-list').List;
var Spinner = require(
  'polythene-mithril-material-design-spinner').MaterialDesignSpinner;

var PartnerInfo = require('./partnerinfo');
var ContractInfo = require('./contract');
var Questionnaire = require('./questionnaire');
var Login = require('./login');

var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

var websock = null;


CallInfo.file_info = {};
CallInfo.search = "";
var log_calls = [];

var actualitzant_reclamacions = false;

var refresh = true;
var search_by = "phone";

var clearCallInfo = function() {
  Questionnaire.call.phone = "";
  Questionnaire.call.log_call_reasons = [];
  Questionnaire.call.reason = "";
  Questionnaire.call.extra = "";
  Questionnaire.call.proc = false;
  Questionnaire.call.improc = false;
  ContractInfo.main_contract = 0;
  desar = "Desa";
  CallInfo.file_info = {};
}

var getInfo = function () {
  m.request({
    method: 'GET',
    url: '/api/info/'+search_by+"/"+CallInfo.search,
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ", response);
    if (response.info.message !== "ok" ) {
      if(response.info.message === "response_too_long") {
        CallInfo.file_info = { 1: "toomuch" };
      }
      else {
        CallInfo.file_info = {}
      }
      console.debug("Error al obtenir les dades: ", response.info.message)
    }
    else{
      CallInfo.file_info=response.info.info;
      if (Questionnaire.call.date === "") {
        Questionnaire.call.date = new Date().toISOString();
      }
    }
  }, function(error) {
    console.debug('Info GET apicall failed: ', error);
  });
};


var updateClaims = function() {
  m.request({
    method: 'GET',
    url: '/api/updateClaims',
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ",response);
    if (response.info.message !== "ok" ) {
      console.debug("Error al actualitzar les reclamacions: ", response.info.message)
    }
    else{
      actualitzant_reclamacions = false;
      Questionnaire.getClaims; // TODO: This seems a noop
    }
  }, function(error) {
    console.debug('Info GET apicall failed: ', error);
  });
};


CallInfo.getLogPerson = function () {
  log_calls = []
  var extension = Login.currentExtension();
  if (extension === -1) {
    return 0
  }
  log_calls.push("lookingfor")
  m.request({
    method: 'GET',
    url: '/api/personlog/' + extension,
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ",response)
    if (response.info.message !== "ok" ) {
      console.debug("Error al obtenir trucades ateses.", response.info.message)
      log_calls = []
    }
    else{
      log_calls = response.info.info
    }
  }, function(error) {
    log_calls = []
    console.debug('Info GET apicall failed: ', error)
  });
};

if(Questionnaire.call.ext !== "" && Questionnaire.call.ext !== -1){
  CallInfo.getLogPerson()
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

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
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
      m('span.partner', info.partner ? info.partner : "Sense informació") : '', 
    (info.motius && info.contracte)? [
      m.trust('&nbsp;'),
      m('span.contract', info.contracte)
    ]:'',
    !info.motius ? m('span.pending', " Pendent d'anotar"):'',
    ''
  );
}

var atencionsLog = function() {
  var aux = [];

  if (log_calls.length === 0) {
    return m(".logs-person", m(List, {
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
  items = log_calls.slice(0).reverse().map(function(item, index) {
    var itemClicked = function(ev) {
        if (item.data === Questionnaire.call.date) {
          clearCallInfo();
          Questionnaire.call.date = "";
        }
        else {
          Questionnaire.call.date = item.data;
          refreshCall(item.telefon);
        }
    }
    var missatge = responsesMessage(item);
    var solved = item.motius != "";
    return m(ListTile, {
      className: (
        ! solved ? "registres" : (
        Questionnaire.call.date == item.data ?  "registres-red-selected" :
        "registres-red"
      )),
      className: "registres",
      selectable: !solved,
      hoverable: !solved,
      ink: true,
      ripple: {
        opacityDecayVelocity: '0.5',
      },
      selected: Questionnaire.call.date == item.data,
      title: missatge,
      subtitle: item.motius,
      events: solved? undefined : { onclick: itemClicked },
      disabled: !refresh,
    });
  })
  return m(".logs-person", m(List, {compact: true, tiles: items}));
}

var logPerson = function() {
  return m(Card, {
    className: 'card-log-person',
    content: [
      { primary: {
        title: m(".title", [ 'Trucades ateses:' ])
      } },
      { text: {
        content: (log_calls[0] === "lookingfor" ?
          m('center', m(Spinner, { show: "true" } )) : atencionsLog())
      }},
    ]
  });
}

var infoPhone = function () {
  if (isEmpty(CallInfo.file_info)) {
    return m('.plane-info', m("body", 'No hi ha informació.'));
  }
  else if (CallInfo.file_info[1] === "empty"){
    return m('.plane-info', m(Spinner, { show: "true" } ));
  }
  else if (CallInfo.file_info[1] === "toomuch"){
    return m('.plane-info',
      m("body", 'Cerca poc específica, retorna masses resultats.')
    );
  } else {
    return m('.call-info', [
      m('.plane-info', PartnerInfo.allInfo(CallInfo.file_info)),
      ContractInfo.listOfContracts(
        CallInfo.file_info,
        PartnerInfo.main_partner
      ),
    ]);
  }
};

var refreshCall = function(phone) {
  clearCallInfo();
  Questionnaire.call.phone = phone;
  CallInfo.search = phone;
  CallInfo.file_info = { 1: "empty" };
  PartnerInfo.main_partner = 0;
  search_by = "phone";
  getInfo();
}

CallInfo.refreshIden = function(new_me) {
  if (!refresh && (new_me.iden !== "" || new_me.iden !== -1)) {
    return 0
  }
  CallInfo.search = ""
  clearCallInfo()
  Questionnaire.call.date = ""
  CallInfo.file_info = {}
  log_calls = []
  Questionnaire.call.iden = new_me.iden
  Questionnaire.call.ext = new_me.ext
  if (Questionnaire.call.ext === -1) {
    refresh = true
  }
}

CallInfo.refreshPhone = function(phone, date) {
  if (refresh) {
    Questionnaire.call.date = date;
    Questionnaire.call.phone = phone;
    search_by = "phone"
    CallInfo.search = phone
    CallInfo.file_info[1] = "empty"
    getInfo();
  }
}

var lookForPhoneInfo = function() {
  clearCallInfo();
  if (CallInfo.search !== 0 && CallInfo.search !== ""){
    Questionnaire.call.phone = "";
    CallInfo.file_info = { 1: "empty" };
    PartnerInfo.main_partner = 0;
    getInfo();
  }
  else {
    Questionnaire.call.date = "";
    CallInfo.file_info = {}
  }
}

var lockCall = function() {
  return m(".num-entrant", [
    m(".text-info", [
      m(".label-text", "Número: "),
      m(".normal-text", Questionnaire.call['phone']),
      m(Button, {
        className: 'btn-lock',
        label: (refresh ? lockIcon() : lockedIcon()),
        border: 'true',
        events: {
          onclick: function() {
            refresh = !refresh
          },
        },
      }, m(Ripple)),
      m(Button, {
        className: "btn-new-tab",
        label: newTabIcon(),
        url: {
          href: window.location,
          target:"_blank",
        },
        border: 'true',
      }, m(Ripple)),
      settings(),
    ]),
  ]);
}

var typeOfSearch = function() {
  return m("select",
    {
      id: "search-by",
      className: ".select-search",
      onchange: function() {
        search_by = document.getElementById("search-by").value;
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

var kalinfoBrowser = function() {
  return m('.busca-info', [
    m(".busca-info-title", [
      typeOfSearch(),
      m(".label", "Cercador: "),
      m(Textfield, {
        className: 'txtf-phone',
        onChange: function(state) {
          CallInfo.search = state.value;
        },
        events: {
          onkeypress: function(event){
            uniCharCode(event)
          }
        },
        disabled: !refresh,
      }),
      m(Button, {
        className: 'btn-search',
        label: searchIcon(),
        events: {
          onclick: function() {
            lookForPhoneInfo();
          },
        },
        disabled: !refresh,
      }, m(Ripple)),
    ]),
  ]);
}

function uniCharCode(event) {
  var char = event.which || event.keyCode;
  if (char === 13) {
    lookForPhoneInfo();
  }
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
        disabled: actualitzant_reclamacions,
        events: {
          onclick: function() {
            actualitzant_reclamacions = true;
            updateClaims();
          },
        },
      }, m(Ripple)),
      actualitzant_reclamacions ? [
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

var settings = function() {
  return m(Button, {
    className: 'btn-settings',
    label: settingsIcon(),
    border: 'true',
    events: {
      onclick: function() {
        settingsDialog();
      },
    },
  }, m(Ripple));
}


CallInfo.mainPage = function() {
  return m('', [
    m(Card, {
      content: [{
        primary: {
          title: m('',[
            kalinfoBrowser(),
            Questionnaire.infoQuestionnaire(
              (isEmpty(CallInfo.file_info) || CallInfo.file_info[1] === "toomuch") && Questionnaire.call.date !== ""
            ),
            lockCall(),
          ]),
        },
      }],
    }),
    m(".all-info-call", [
      infoPhone(),
      m("", logPerson())
    ])
  ]);
}

var getServerSockInfo = function() {
    m.request({
        method: 'GET',
        url: '/api/socketInfo',
        extract: deyamlize,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error get data: ", response.info.message);
            return;
        }
        var port = response.info.port_ws;
        connectWebSocket(port);
    }, function(error) {
        console.debug('Info GET apicall failed WebSock: ', error);
    });
}
getServerSockInfo();

var connectWebSocket = function(port) {
    var addr = 'ws://'+window.location.hostname+':'+port+'/';
    websock = new WebSocket(addr);
    websock.onopen = CallInfo.sendIdentification;
    websock.onmessage = function (event) {
        var message = event.data.split(":");
        var type_of_message = message[0];
        if (type_of_message === "IDEN") {
            var iden = message[1];
            var ext = Login.currentExtension();
            var info = {
                iden: iden,
                ext: ext,
            }
            CallInfo.refreshIden(info);
            CallInfo.getLogPerson();
        }
        else if (type_of_message === "PHONE") {
            var phone = message[1];
            var date = message[2]+":"+message[3]+":"+message[4];
            CallInfo.refreshPhone(phone, date);
            CallInfo.getLogPerson();
        }
        else if (type_of_message === "REFRESH") {
            CallInfo.getLogPerson();
        }
        else {
            console.debug("Message recieved from WebSockets and type not recognized.");
        }
    }
}

CallInfo.sendIdentification = function() {
    message = "IDEN:"+Login.getMyExt()+":"+Login.myName()+":";
    websock.send(message);
}


Login.onLogin.push(CallInfo.sendIdentification);
Login.onLogout.push(CallInfo.sendIdentification);
Login.onLogout.push(CallInfo.refreshIden);
Login.onLogout.push(CallInfo.getLogPerson);

return CallInfo;

}();

// vim: et ts=2 sw=2
