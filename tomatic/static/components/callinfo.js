'use strict';

module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var Login = require('./login');

var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

var websock = null;
CallInfo.topics = [];
CallInfo.sections = [];
CallInfo.search = ""; // Search value
CallInfo.search_by = "phone"; // Search file
CallInfo.searchResults = {}; // Retrieved search data
CallInfo.currentPerson = 0; // Selected person from search data
CallInfo.currentContract = 0; // Selected contract selected person
CallInfo.callLog = []; // User call registry
CallInfo.updatingClaims = false; // Whether we are still loading claim types
CallInfo.updatingCrmCategories = false; // Whether we are still loading crm categoies
CallInfo.autoRefresh = true; // whether we are auto searching on incomming calls
CallInfo.call = {
    'phone': "", // phone of the currently selected call registry
    'date': "", // isodate of the last unbinded search or the currently selected call registry
    'topic': "", // annotated topic for the call
    'notes': "", // annotated comments for the call
};
CallInfo.call_reasons = {
    'general': [],
    'infos': [],
    'extras': []
}
CallInfo.keyword2topic = {};

CallInfo.savingAnnotation = false;
CallInfo.annotation = {};

CallInfo.resetAnnotation = function() {
  var tag = CallInfo.reasonTag()
  CallInfo.annotation = {
    resolution: 'unsolved',
    tag: tag,
  }
};

CallInfo.noSection = "ASSIGNAR USUARI";
CallInfo.helpdeskSection = "CONSULTA";
CallInfo.hasNoSection = function() {
  return CallInfo.annotation.tag === CallInfo.noSection;
};
CallInfo.reasonTag = function() {
  var topic = CallInfo.call.topic;
  var matches = topic.match(/\[(.*?)\]/);
  if (matches) {
    return matches[1].trim();
  }
  return "";
};

var postAnnotation = function(annotation) {
  m.request({
    method: 'POST',
    url: '/api/call/annotate',
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
      CallInfo.call.notes = "";
      CallInfo.call.date = "";
    }
  }, function(error) {
    console.debug('Info POST apicall failed: ', error);
  });
  CallInfo.call.topic = "";
}

CallInfo.annotationIsClaim = function() {
  return CallInfo.reasonTag() !== CallInfo.helpdeskSection;
}

CallInfo.saveCallLog = function(claim) {
  CallInfo.savingAnnotation = true;
  var partner = CallInfo.selectedPartner();
  var contract = CallInfo.selectedContract();
  var user = Login.myName();
  var partner_code = partner!==null ? partner.id_soci : "";
  var contract_number = contract!==null ? contract.number : "";
  var isodate = CallInfo.call.date || new Date().toISOString();
  var isClaim = CallInfo.annotationIsClaim();
  var claim = CallInfo.annotation;
  postAnnotation({
    "user": user,
    "date": isodate,
    "phone": CallInfo.call.phone,
    "partner": partner_code,
    "contract": contract_number,
    "reason": CallInfo.call.topic,
    "notes": CallInfo.call.notes,
    "claimsection": (
      !isClaim ? "" : (
      claim.tag ? claim.tag : (
      CallInfo.helpdeskSection
    ))),
    "resolution": isClaim ? claim.resolution:'',
  });
}

CallInfo.clear = function() {
  CallInfo.call.phone = "";
  CallInfo.call.topic = "";
  CallInfo.call.notes = "";
  CallInfo.currentPerson = 0;
  CallInfo.currentContract = 0;
  CallInfo.savingAnnotation = false;
  CallInfo.searchResults = {};
}


CallInfo.changeUser = function(newUser) {
  CallInfo.search = "";
  CallInfo.clear();
  CallInfo.call.date = "";
  CallInfo.searchResults = {};
  CallInfo.callLog = [];
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
  CallInfo.searchResults = { 1: "empty" };
  retrieveInfo();
}

CallInfo.selectableSections = function() {
  return CallInfo.sections.map(function(section) {
    return section.name;
  });
};

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
    return CallInfo.keyword2topic[extra];
  });
};

CallInfo.filteredTopics = function(filter) {
  var lowerFilter = filter.toLowerCase()
  return CallInfo.topics
    .filter(function(topic) {
      if (topic.description.toLowerCase().includes(lowerFilter)) {
        return true;
      }
      if (topic.keywords.toLowerCase().includes(lowerFilter)) {
        return true;
      }
      return false;
    })
    .map(function(topic) {
      return topic.description;
    });
};

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

CallInfo.searchStatus = function() {
  if (isEmpty(CallInfo.searchResults)) {
    return "ZERORESULTS";
  }
  if (CallInfo.searchResults[1] === "empty") {
    return "SEARCHING";
  }
  if (CallInfo.searchResults[1] === "toomuch") {
    return "TOOMANYRESULTS";
  }
  return "SUCCESS"
}

CallInfo.selectedPartner = function() {
  if (!CallInfo.searchResults) { return null; }
  if (!CallInfo.searchResults.partners) { return null; }
  if (CallInfo.searchResults.partners.length===0) { return null; }
  var partner = CallInfo.searchResults.partners[CallInfo.currentPerson];
  if (partner === undefined) { return null; }
  return partner;
};


CallInfo.selectedContract = function() {
  var partner = CallInfo.selectedPartner();
  if (partner === null) { return null; }
  if (partner.contracts === undefined) { return null; }
  if (partner.contracts.length === 0) { return null; }
  return partner.contracts[CallInfo.currentContract];
};


CallInfo.selectContract = function(idx) {
  CallInfo.currentContract = idx;
};


var retrieveInfo = function () {
  m.request({
    method: 'GET',
    url: '/api/info/'+CallInfo.search_by+"/"+encodeURIComponent(CallInfo.search.trim()),
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ", response);
    if(response.info.message === "response_too_long") {
      CallInfo.searchResults = { 1: "toomuch" };
      return;
    }
    if (response.info.message !== "ok" ) {
      console.debug("Error al obtenir les dades: ", response.info.message)
      CallInfo.searchResults = {}
      return;
    }

    CallInfo.searchResults=response.info.info;
    if (CallInfo.call.date === "") { // TODO: If selection is none
      CallInfo.call.date = new Date().toISOString();
    }
    // Keep the context, just in case a second query is started
    // and CallInfo.searchResults is overwritten
    var context = CallInfo.searchResults;
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
          contract.atr_cases = retrieved.atr_cases;
        })
      })
    });
  }, function(error) {
    console.debug('Info GET apicall failed: ', error);
  });
};

CallInfo.getTopics = function() {
  m.request({
      method: 'GET',
      url: '/api/call/annotate/topics',
      extract: deyamlize,
  }).then(function(response){
      console.debug("Topics GET Response: ",response);

      CallInfo.topics = response.categories;
      CallInfo.topics.map(function(topic) {
          var section = topic.section;
          if (section === null) {
              section = CallInfo.noSection;
          }
          if (section === "HelpDesk") {
              section = CallInfo.helpdeskSection;
          }
          topic.description = "["+section+"] "+topic.code+". "+topic.name;
      })
      CallInfo.sections = response.sections;
  }, function(error) {
      console.debug('Info GET apicall failed: ', error);
  });
}

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
      else {
        CallInfo.call_reasons.general = response.info.claims;
        CallInfo.keyword2topic = response.info.dict;
        CallInfo.call_reasons.extras = Object.keys(response.info.dict);
      }
  }, function(error) {
      console.debug('Info GET apicall failed: ', error);
  });
};


CallInfo.getInfos = function() {
  m.request({
      method: 'GET',
      url: '/api/getInfos',
      extract: deyamlize,
  }).then(function(response){
      console.debug("Info GET Response: ",response);
      if (response.info.message !== "ok" ) {
          console.debug("Error al obtenir els infos: ", response.info.message)
      }
      else {
        CallInfo.call_reasons.infos = response.info.infos;
      }
  }, function(error) {
      console.debug('Info GET apicall failed: ', error);
  });
};


CallInfo.updateClaims = function() {
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

CallInfo.updateCrmCategories = function() {
  CallInfo.updatingCrmCategories = true;
  m.request({
    method: 'GET',
    url: '/api/updateCrmCategories',
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ",response);
    if (response.info.message !== "ok" ) {
      console.debug("Error al actualitzar les categories de trucades telefòniques: ", response.info.message)
    }
    else{
      CallInfo.updatingCrmCategories = false;
      CallInfo.getInfos();
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
    CallInfo.searchResults = { 1: "empty" };
    CallInfo.currentPerson = 0;
    retrieveInfo();
  }
  else {
    CallInfo.call.date = "";
    CallInfo.searchResults = {}
  }
}


var connectWebSocket = function() {
    var url = new URL('/backchannel', window.location.href);
    url.protocol = url.protocol.replace('http', 'ws');
    console.log("Connecting WS",url.href)
    websock = new WebSocket(url.href);
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
CallInfo.getTopics();
CallInfo.getClaims();
CallInfo.getInfos();
CallInfo.getLogPerson()

Login.onLogin.push(CallInfo.sendIdentification);
Login.onLogin.push(CallInfo.getLogPerson);
Login.onLogout.push(CallInfo.sendIdentification);
Login.onLogout.push(CallInfo.getLogPerson);
Login.onUserChanged.push(CallInfo.changeUser);
Login.onUserChanged.push(CallInfo.getLogPerson);
connectWebSocket();

return CallInfo;

}();

// vim: et ts=2 sw=2
