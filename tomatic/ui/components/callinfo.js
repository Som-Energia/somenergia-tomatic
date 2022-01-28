'use strict';

module.exports = function() {

var m = require('mithril');
var deyamlize = require('./utils').deyamlize;

var Login = require('./login');

var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

var websock = null;
CallInfo.categories = []; // Call categories
CallInfo.sections = []; // Teams to assign a call
CallInfo.search = ""; // Search value
CallInfo.search_by = "phone"; // Search criteria
CallInfo.searchResults = {}; // Retrieved search data
CallInfo.currentPerson = 0; // Selected person from search data
CallInfo.currentContract = 0; // Selected contract selected person
CallInfo.callLog = []; // User call registry
CallInfo.updatingCategories = false; // Whether we are still loading crm categoies
CallInfo.autoRefresh = true; // whether we are auto searching on incomming calls
CallInfo.call = {
    'phone': "", // phone of the currently selected call registry
    'date': "", // isodate of the last unbinded search or the currently selected call registry
    'category': "", // annotated category for the call
    'notes': "", // annotated comments for the call
};

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
  var category = CallInfo.call.category;
  var matches = category.match(/\[(.*?)\]/);
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
      CallInfo.call.date = "";
      CallInfo.clearAnnotation();
    }
  }, function(error) {
    console.debug('Info POST apicall failed: ', error);
  });
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
    "reason": CallInfo.call.category,
    "notes": CallInfo.call.notes,
    "claimsection": (
      !isClaim ? "" : (
      claim.tag ? claim.tag : (
      CallInfo.helpdeskSection
    ))),
    "resolution": isClaim ? claim.resolution:'',
  });
}

CallInfo.clearAnnotation = function() {
  CallInfo.call.category = "";
  CallInfo.call.notes = "";
  CallInfo.savingAnnotation = false;
};

// Nicely clears search results
CallInfo.resetSearch = function() {
  CallInfo.currentPerson = 0;
  CallInfo.currentContract = 0;
  CallInfo.searchResults = {};
};

CallInfo.changeUser = function(newUser) {
  CallInfo.search = "";
  // clear
  CallInfo.call.phone = "";
  CallInfo.clearAnnotation();
  CallInfo.resetSearch();
  // end of clear
  CallInfo.call.date = "";
  CallInfo.callLog = [];
  CallInfo.autoRefresh = true;
}


CallInfo.callReceived = function(date, phone) {
  if (!CallInfo.autoRefresh) { return; }
  CallInfo.callSelected(date,phone)
}


CallInfo.callSelected = function(date, phone) {
  // clear
  CallInfo.clearAnnotation();
  CallInfo.resetSearch();
  // end of clear
  CallInfo.call.date = date;
  CallInfo.call.phone = phone;
  CallInfo.search = phone;
  CallInfo.search_by = "phone";
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


CallInfo.filteredCategories = function(filter) {
  var lowerFilter = filter.toLowerCase()
  return CallInfo.categories
    .filter(function(category) {
      if (category.description.toLowerCase().includes(lowerFilter)) {
        return true;
      }
      if (category.keywords.toLowerCase().includes(lowerFilter)) {
        return true;
      }
      return false;
    })
    .map(function(category) {
      return category.description;
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
  CallInfo.searchResults = { 1: "empty" }; // Searching...
  var encodedValue = encodeURIComponent(CallInfo.search.trim());
  m.request({
    method: 'GET',
    url: '/api/info/'+CallInfo.search_by+"/"+encodedValue,
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

CallInfo.getCategories = function() {
  m.request({
      method: 'GET',
      url: '/api/call/categories',
      extract: deyamlize,
  }).then(function(response){
      console.debug("Categories GET Response: ",response);

      CallInfo.categories = response.categories;
      CallInfo.categories.map(function(category) {
          var section = category.section;
          if (section === null) {
              section = CallInfo.noSection;
          }
          if (section === "HelpDesk") {
              section = CallInfo.helpdeskSection;
          }
          category.description = "["+section+"] "+category.code+". "+category.name;
      })
      CallInfo.sections = response.sections;
  }, function(error) {
      console.debug('Info GET apicall failed: ', error);
  });
}

CallInfo.updateCategories = function() {
  CallInfo.updatingCategories = true;
  m.request({
    method: 'GET',
    url: '/api/call/categories/update',
    extract: deyamlize,
  }).then(function(response){
    console.debug("Info GET Response: ",response);
    if (response.info.message !== "ok" ) {
      console.debug("Error al actualitzar les categories de trucades telefòniques: ", response.info.message)
    }
    else{
      CallInfo.updatingCategories = false;
      CallInfo.getCategories();
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
  // clear
  CallInfo.call.phone = "";
  CallInfo.call.clearAnnotation();
  CallInfo.resetSearch();
  // end of clear
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
  // clear
  CallInfo.clearAnnotation();
  CallInfo.resetSearch();
  // end of clear
  if (CallInfo.search !== 0 && CallInfo.search !== ""){
    retrieveInfo();
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
CallInfo.getCategories();
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
