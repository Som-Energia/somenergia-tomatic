
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Ripple = require('polythene-mithril-ripple').Ripple;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var Textfield = require('polythene-mithril-textfield').TextField;
var Card = require('polythene-mithril-card').Card;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var List = require ('polythene-mithril-list').List;
var Icon = require ('polythene-mithril-icon').Icon;
var Spinner = require('polythene-mithril-material-design-spinner').MaterialDesignSpinner;

var Login = require('./login');
var Proves = require('./proves');
var styleCallinfo = require('./callinfo_style.styl');
var CallInfo = {};

CallInfo.file_info = {};
CallInfo.phone = "";
CallInfo.ws = null;
CallInfo.iden = "0";


CallInfo.getInfo = function () {
    var data = CallInfo.phone;
    m.request({
        method: 'GET',
        url: '/api/info/'+data,
        data: data,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            CallInfo.file_info = {}
            console.debug("Error al obtenir les dades: ", response.info.message)
        }
        else{
            CallInfo.file_info=response.info.info;
        }
    }, function(error) {
        console.debug('Info GET apicall failed: ', error);
    });
};


CallInfo.openServerSock = function() {
    m.request({
        method: 'GET',
        url: '/api/info/openSock',
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info POST Response: ",response);
        if (response.info.message === "ok" ) {
            console.debug("Creat WebSocket a @IP=192.168.35.11 #port=4556");
        } else if (response.info.message === "done") {
            console.debug("WebSocket was already oppened.");
        } else{
            console.debug("Error al obtenir les dades: ", response.info.message);
        }
    }, function(error) {
        console.debug('Info GET apicall failed WebSock: ', error);
    });
}


function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}


CallInfo.infoPhone = function () {
    if (isEmpty(CallInfo.file_info)) {
        return m('center', m("body", 'No hi ha informació.'));
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m('center',m(Spinner, { show: "true" } ));
    } else {
        return m('', Proves.allInfo(CallInfo.file_info));
    }
};


CallInfo.connectWebSocket = function() {

    var addr = 'ws://192.168.35.11:4556/';
    if(CallInfo.ws !== null) {
        CallInfo.clearInfo();
    }
    CallInfo.ws = new WebSocket(addr);
    var ws = CallInfo.ws;

    ws.onopen = function(event) {
        var ext = Login.getMyExt();
        ws.send(ext);
    }

    ws.onmessage = function (event) {
        var content = event.data;
        if(content === 'warning'){
            alert("Persona ja identificada!!");
            Login.disconnect();
        } else {
            CallInfo.phone = content;
            CallInfo.getInfo();
        }
    }
}


CallInfo.clearInfo = function() {
    CallInfo.phone = "";
    CallInfo.file_info = {};
    if(CallInfo.ws !== null){
        var ws = CallInfo.ws;
        ws.close();
        CallInfo.ws = null;
    }
}


CallInfo.mainPage = function() {

    var info = Login.whoAreYou();
    var nom = "IDENTIFICAR";
    var color = "#FFFFFF";


    if (info !== ":") {
        var aux = info.split(":");
        var id = aux[0];
        nom = Login.getName(id);
        color = "#" + aux[2];
        if(CallInfo.iden !== nom || CallInfo.ws === null){
            CallInfo.connectWebSocket();
            CallInfo.iden = nom;
        }
    }

    return m( '', [
            m("div", { class: 'info' }, [
                "Número: ",
                m(Textfield, {
                    class: 'txtf-phone',
                    onChange: function(state) {
                        CallInfo.phone = state.value;
                    }
                }),
                m(Button, {
                    class: 'btn-search',
                    label: "🔎",
                    events: {
                        onclick: function() {
                            if(CallInfo.phone!==0 && CallInfo.phone!==""){
                                CallInfo.file_info = { 1: "empty" }
                                CallInfo.getInfo();
                            } 
                            else {
                                 CallInfo.file_info = {}
                            }
                        },
                    }
                }, m(Ripple)),
                m(Button, {
                    class: 'btn-connect',
                    label: nom,
                    border: true,
                    events: {
                        onclick: function() {
                            if(CallInfo.iden == "0"){
                                CallInfo.openServerSock();
                                CallInfo.iden = "";
                            }
                            Login.askWhoAreYou();
                        },
                    },
                    style: { backgroundColor: color },
                }, m(Ripple)),
                m(Button, {
                    class: 'btn-disconnect',
                    label: '❌',
                    events: {
                        onclick: function() {
                            CallInfo.clearInfo();
                            Login.disconnect();
                        }
                    }
                }, m(Ripple)),
            ]),
            m("div", " "),
            m("div", CallInfo.infoPhone())
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
