module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var PartnerInfo = require('./partnerinfo');
var ContractInfo = require('./contract');
var Questionnaire = require('./questionnaire');
var Login = require('./login');

var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

var websock = null;
CallInfo.file_info = {};
CallInfo.search = "";
CallInfo.callLog = [];
CallInfo.updatingClaims = false;
CallInfo.refresh = true;
CallInfo.search_by = "phone";

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
    url: '/api/info/'+CallInfo.search_by+"/"+CallInfo.search,
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
      Questionnaire.getClaims; // TODO: This seems a noop
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

if(Questionnaire.call.ext !== "" && Questionnaire.call.ext !== -1){
  CallInfo.getLogPerson()
}

var refreshCall = function(phone) {
  clearCallInfo();
  Questionnaire.call.phone = phone;
  CallInfo.search = phone;
  CallInfo.file_info = { 1: "empty" };
  PartnerInfo.main_partner = 0;
  CallInfo.search_by = "phone";
  getInfo();
}

CallInfo.refreshIden = function(new_me) {
  if (!CallInfo.refresh && (new_me.iden !== "" || new_me.iden !== -1)) {
    return 0
  }
  CallInfo.search = ""
  clearCallInfo()
  Questionnaire.call.date = ""
  CallInfo.file_info = {}
  CallInfo.callLog = []
  Questionnaire.call.iden = new_me.iden
  Questionnaire.call.ext = new_me.ext
  if (Questionnaire.call.ext === -1) {
    CallInfo.refresh = true
  }
}

CallInfo.refreshPhone = function(phone, date) {
  if (CallInfo.refresh) {
    Questionnaire.call.date = date;
    Questionnaire.call.phone = phone;
    CallInfo.search_by = "phone"
    CallInfo.search = phone
    CallInfo.file_info[1] = "empty"
    getInfo();
  }
}

CallInfo.searchCustomer = function() {
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
    websock.onopen = CallInfo.sendIdentification;
    websock.onmessage = CallInfo.onMessageReceived;
}

CallInfo.sendIdentification = function() {
    message = "IDEN:"+Login.getMyExt()+":"+Login.myName()+":";
    websock.send(message);
}

CallInfo.onMessageReceived = function(event) {
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
        return;
    }
    if (type_of_message === "PHONE") {
        var phone = message[1];
        var date = message[2]+":"+message[3]+":"+message[4];
        CallInfo.refreshPhone(phone, date);
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
Login.onLogout.push(CallInfo.refreshIden);
Login.onLogout.push(CallInfo.getLogPerson);

return CallInfo;

}();

// vim: et ts=2 sw=2
