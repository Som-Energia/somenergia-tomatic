'use strict';

module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var Login = require('./login');

var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

var websock = null;
CallInfo.search = ""; // Search value
CallInfo.search_by = "phone"; // Search file
CallInfo.file_info = {}; // Retrieved search data
CallInfo.currentPerson = 0; // Selected person from search data
CallInfo.currentContract = 0; // Selected contract selected person
CallInfo.callLog = []; // User call registry
CallInfo.updatingClaims = false; // Whether we are still loading claim types
CallInfo.autoRefresh = true; // whether we are auto searching on incomming calls
CallInfo.call = {
    'phone': "", // phone of the currently selected call registry
    'date': "", // isodate of the last unbinded search or the currently selected call registry
    'reason': "", // annotated reason for the call
    'extra': "", // annotated comments for the call
    'log_call_reasons': [],
};
CallInfo.call_reasons = {
    'general': [],
    'infos': [],
    'extras': []
}
CallInfo.extras_dict = {};
CallInfo.savingAnnotation = false;

CallInfo.clear = function() {
  CallInfo.call.phone = "";
  CallInfo.call.log_call_reasons = [];
  CallInfo.call.reason = "";
  CallInfo.call.extra = "";
  CallInfo.call.proc = false;
  CallInfo.call.improc = false;
  CallInfo.currentPerson = 0;
  CallInfo.currentContract = 0;
  CallInfo.savingAnnotation = false;
  CallInfo.file_info = {};
}

CallInfo.changeUser = function(newUser) {
  CallInfo.search = "";
  CallInfo.clear();
  CallInfo.call.date = "";
  CallInfo.file_info = {};
  CallInfo.callLog = [];
  CallInfo.call.iden = newUser;
  CallInfo.autoRefresh = true;
}

CallInfo.callReceived = function(date, phone) {
  if (!CallInfo.autoRefresh) { return; }
  CallInfo.callSelected(date,phone)
}

CallInfo.callSelected = function(date, phone) {
  CallInfo.clear();
  CallInfo.call.date = date;
  CallInfo.call.phone = phone;
  CallInfo.search = phone;
  CallInfo.search_by = "phone";
  CallInfo.file_info = { 1: "empty" };
  retrieveInfo();
}



function formatContractNumber(number) {
  // some contract numbers get converted  to int and lose their padding
  var result = number+"";
  while (result.length < 7) result = "0" + result;
  return result;
}

function contractNumbers(info) {
  var result = {}
  info.partners.map(function(partner) {
    partner.contracts.map(function(contract) {
      var number = formatContractNumber(contract.number);
      result[number] = contract;
    })
  })
  return Object.keys(result);
}

CallInfo.getExtras = function (extras) {
  return extras.map(function(extra) {
    return CallInfo.extras_dict[extra];
  });
}

var retrieveInfo = function () {
  m.request({
    method: 'GET',
    url: '/api/info/'+CallInfo.search_by+"/"+CallInfo.search,
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ", response);
    if(response.info.message === "response_too_long") {
      CallInfo.file_info = { 1: "toomuch" };
      return;
    }
    if (response.info.message !== "ok" ) {
      console.debug("Error al obtenir les dades: ", response.info.message)
      CallInfo.file_info = {}
      return;
    }

    CallInfo.file_info=response.info.info;
    if (CallInfo.call.date === "") { // TODO: If selection is none
      CallInfo.call.date = new Date().toISOString();
    }
    // Keep the context, just in case a second query is started
    // and CallInfo.file_info is overwritten
    var context = CallInfo.file_info;
    m.request({
      method: 'POST',
      url: '/api/info/contractdetails',
      extract: deyamlize,
      body: {
        contracts: contractNumbers(context),
      },
    }).then(function(response) {
      context.partners.map(function(partner) {
        partner.contracts.map(function(contract) {
          var number = formatContractNumber(contract.number);
          var retrieved = response.info.info[number]
          contract.invoices = retrieved.invoices;
          contract.lectures_comptadors = retrieved.lectures_comptadors;
        })
      })
    });
  }, function(error) {
    console.debug('Info GET apicall failed: ', error);
  });
};

CallInfo.getClaims = function() {
  m.request({
      method: 'GET',
      url: '/api/getClaims',
      extract: deyamlize,
  }).then(function(response){
      console.debug("Info GET Response: ",response);
      if (response.info.message !== "ok" ) {
          console.debug("Error al obtenir les reclamacions: ", response.info.message)
      }
      else{
        CallInfo.call_reasons.general = response.info.claims;
        CallInfo.extras_dict = response.info.dict;
        CallInfo.call_reasons.extras = Object.keys(response.info.dict);
      }
  }, function(error) {
      console.debug('Info GET apicall failed: ', error);
  });
};
CallInfo.getClaims();

var updateClaims = function() {
  CallInfo.updatingClaims = true;
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
      CallInfo.updatingClaims = false;
      CallInfo.getClaims();
    }
  }, function(error) {
    console.debug('Info GET apicall failed: ', error);
  });
};


CallInfo.getLogPerson = function () {
  CallInfo.callLog = []
  var extension = Login.currentExtension();
  if (extension === -1) {
    return 0
  }
  CallInfo.callLog.push("lookingfor")
  m.request({
    method: 'GET',
    url: '/api/personlog/' + extension,
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ",response)
    if (response.info.message !== "ok" ) {
      console.debug("Error al obtenir trucades ateses.", response.info.message)
      CallInfo.callLog = []
    }
    else{
      CallInfo.callLog = response.info.info
    }
  }, function(error) {
    CallInfo.callLog = []
    console.debug('Info GET apicall failed: ', error)
  });
};

CallInfo.getLogPerson()

CallInfo.isLogSelected = function(date) {
  return CallInfo.call.date === date;
}
CallInfo.selectLog = function(date, phone) {
  //console.log("Selecting", date, phone, CallInfo.call.date);
  CallInfo.callSelected(date, phone);
}
CallInfo.deselectLog = function() {
  //console.log("deselecting", CallInfo.call.date);
  CallInfo.clear();
  CallInfo.call.date = "";
  CallInfo.search = "";
}
CallInfo.toggleLog = function(date, phone) {
  //console.log("Toggling", date, phone, CallInfo.call.date);
  if (CallInfo.isLogSelected(date)) {
    CallInfo.deselectLog();
  }
  else {
    CallInfo.selectLog(date, phone);
  }
}

CallInfo.searchCustomer = function() {
  CallInfo.clear();
  if (CallInfo.search !== 0 && CallInfo.search !== ""){
    CallInfo.call.phone = "";
    CallInfo.file_info = { 1: "empty" };
    CallInfo.currentPerson = 0;
    retrieveInfo();
  }
  else {
    CallInfo.call.date = "";
    CallInfo.file_info = {}
  }
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
/*
var url = new URL('/', window.location.href);
url.protocol = url.protocol.replace('http', 'ws');
var addr = url.href
*/

var connectWebSocket = function(port) {
    var addr = 'ws://'+window.location.hostname+':'+port+'/';
    websock = new WebSocket(addr);
    websock.onmessage = CallInfo.onMessageReceived;
    websock.onopen = CallInfo.sendIdentification;
}

CallInfo.sendIdentification = function() {
    var message = "IDEN:"+Login.myName()+":";
    websock.send(message);
}

CallInfo.onMessageReceived = function(event) {
    console.log("WS:", event.data);
    var message = event.data.split(":");
    var type_of_message = message[0];
    if (type_of_message === "PHONE") {
        var phone = message[1];
        var date = message[2]+":"+message[3]+":"+message[4];
        CallInfo.callReceived(date, phone);
        CallInfo.getLogPerson();
        return;
    }
    if (type_of_message === "REFRESH") {
        CallInfo.getLogPerson();
        return
    }
    console.debug("Message received from WebSockets and type not recognized.");
}

Login.onLogin.push(CallInfo.sendIdentification);
Login.onLogin.push(CallInfo.getLogPerson);
Login.onLogout.push(CallInfo.sendIdentification);
Login.onLogout.push(CallInfo.getLogPerson);
Login.onUserChanged.push(CallInfo.changeUser);
Login.onUserChanged.push(CallInfo.getLogPerson);

return CallInfo;

}();

// vim: et ts=2 sw=2
