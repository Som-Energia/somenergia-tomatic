
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var List = require ('polythene-mithril-list').List;
var Ripple = require('polythene-mithril-ripple').Ripple;

var styleCallinfo = require('./callinfo_style.styl');
var Tomatic = require('./tomatic');
var Callinfo = require('./callinfo');

var Login = {};
var first = 0;
var iden = "0";
var websock = null;


var openServerSock = function() {
    m.request({
        method: 'GET',
        url: '/api/info/openSock',
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message === "ok" ) {
            console.debug("WebSocket created.");
        } else if (response.info.message === "done") {
            console.debug("WebSocket was already oppened.");
        } else{
            console.debug("Error get data: ", response.info.message);
        }
    }, function(error) {
        console.debug('Info GET apicall failed WebSock: ', error);
    });
}


var connectWebSocket = function() {
    var addr = 'ws://192.168.35.11:4556/';
    if(websock !== null) {
        clearInfo();
    }
    websock = new WebSocket(addr);
    var ws = websock;
    ws.onopen = function(event) {
        var ext = getMyExt();
        ws.send(ext);
    }
    ws.onmessage = function (event) {
        var content = event.data;
        Callinfo.refreshInfo(content,iden);
    }
}


var clearInfo = function() {
    Callinfo.refreshInfo("","");
    if(websock !== null){
        var ws = websock;
        ws.close();
        websock = null;
    }
}


Date.prototype.addHours = function(h) {
   this.setTime(this.getTime() + (h*60*60*1000));
   return this;
}


var disconnect = function(){
    document.cookie = "; expires = Thu, 01 Jan 1970 00:00:00 GMT;path=/";
}


var getMyExt = function() {
    var x = document.cookie;
    var aux = x.split(":");
    var ext = aux[1].toString();
    return ext;
}


var setCookieInfo = function(vnode){
    var aux = vnode.attributes;
    var name_button = aux["0"].ownerElement.innerText;
    var persons = Tomatic.persons().extensions;
    var found = false;

    for(id in persons){
        var name = Tomatic.formatName(id);
        if(name.toUpperCase() == name_button) {
            found = true;
            break;
        }
    }
    if(found){
        var value = id + ":" + Tomatic.persons().extensions[id] + ":" + Tomatic.persons().colors[id];
        var exp = new Date().addHours(3);
        var expires = "expires="+ exp.toUTCString();
        document.cookie = value + ";" + expires + ";path=/";
    }
}


var listOfPersons = function() {
    var aux = [];
    var persons = Tomatic.persons().extensions;

    for(id in persons){
        var name = Tomatic.formatName(id);
        var color = "#" + Tomatic.persons().colors[id];
        if(name !== '-' && name !== '>CONTESTADOR<'){
            aux.push(m(Button, { 
                label: name,
                border: true,
                style: { backgroundColor: color, margin: '4px' },
                events: {
                    onclick: function() {
                        setCookieInfo(this);
                        Dialog.hide({id:'whoAreYou'});
                    },
                },
            }));
        }
    }
    return m(List, { tiles:aux, style:{marginBottom:'10px'} });
}


var askWhoAreYou = function() {
    Dialog.show(function() { return {
        //class: 'dialog-login',
        title: 'Qui ets?',
        backdrop: true,
        body: [
            listOfPersons()
        ],
        footerButtons: [
            m(Button, {
                label: "Cancel·la",
                events: {
                    onclick: function() {
                        Dialog.hide({id:'whoAreYou'});
                    },
                },
            }),
        ],
        style: { background: "#FFFFFF", width: '750px', marginLeft: '-180px' },
        didHide: function() {m.redraw();}
    };},{id:'whoAreYou'});
}


var whoAreYou = function() {
    var info = ":";
    var x = document.cookie;
    if (x !== "") {
        info = x;
    }
    return info;
}


Login.identification = function() {
    var info = whoAreYou();
    var nom = "IDENTIFICAR";
    var color = 'rgba(255, 255, 255, 0.7)';

    if (info !== ":") {
        var aux = info.split(":");
        var id = aux[0];
        nom = Tomatic.formatName(id);
        color = "#" + aux[2];
        if(iden !== nom || websock === null){
            connectWebSocket();
            iden = nom;
        }
    }

    return m('', [
        m(Button, {
            label: nom,
            border: true,
            events: {
                onclick: function() {
                    if(first == "0"){
                        openServerSock();
                        first = "";
                    }
                    askWhoAreYou();
                },
            },
            style: { backgroundColor: color },
        }, m(Ripple)),
        m(Button, {
            //class: 'btn-disconnect',
            label: '❌',
            events: {
                onclick: function() {
                    clearInfo();
                    disconnect();
                }
            },
            style: {
                backgroundColor: '#E1232C',
                color: '#A0D8BC',
                marginLeft: '10px',
                width: '30px',
                height: '30px',
                borderRadius: '50%'
            },
        }, m(Ripple)),
    ]);
}



return Login;

}();

// vim: noet ts=4 sw=4
