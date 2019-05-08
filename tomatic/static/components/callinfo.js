
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var Textfield = require('polythene-mithril-textfield').TextField;
var Card = require('polythene-mithril-card').Card;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var List = require ('polythene-mithril-list').List;
var Icon = require ('polythene-mithril-icon').Icon;
var Spinner = require('polythene-mithril-material-design-spinner').MaterialDesignSpinner;

var Login = require('./login');
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


CallInfo.infoPhone = function (name) {
    if (isEmpty(CallInfo.file_info)) {
        return m("body", 'No hi ha informació.')
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m(Spinner, { show: "true" } );
    } else {
        return m('', CallInfo.listOfPartners());
    }
};


CallInfo.listOfPartners = function (name) {
    var partner = 0;
    var numOfPartners = CallInfo.file_info.partners.length;

    var aux = [];

    for (partner; partner < numOfPartners; partner++) {
        aux[partner] = CallInfo.allInfo(partner);
    }

    return m(List, {
      header: { title: "Partners:" },
      tiles: [ aux ],
      style: { marginBottom: '20px' }
    });
}


CallInfo.allInfo = function (partner) {
    var style = {
        maxWidth: "500px",
        backgroundColor: "#FFFFFF",
        marginBottom: '20px',
    }
    var header = {
        title: CallInfo.file_info.partners[partner].name,
        subtitle: CallInfo.file_info.partners[partner].id_soci,
        //icon: getIcon(),
    };
    var media = { // TODO: Grafica generada a partir de la info
        content: CallInfo.generateGraphics(partner),
    }
    var primary = {
        title: CallInfo.file_info.partners[partner].lang,
        subtitle: CallInfo.file_info.partners[partner].email,
    };
    var content = [
        m(Button, { // centrar
            label: "Contractes",
            events: {
                onclick: function() {
                    CallInfo.showContracts(partner);
                },
            },
        })
    ];
    var city = CallInfo.file_info.partners[partner].city;

    return m(Card, {
        style: style,
        content: [
            { header: header },
            { media: media },
            { primary: primary },
            { actions: { content: content } },
            { text: { content: city } }
        ]
    });
}


// TODO
function getIcon() {
    // Mirem estat del client
    var image = "img/avatar.png";
    return {size: "large", avatar: "true", src: image};
}


// TODO
CallInfo.generateGraphics = function(partner) {
    // gestio amb la info del partner per generar imatge
    return m("img", { src: "img/large.png", style: { maxWidth: "360px" } })
}


CallInfo.contractInfo = function(partner, contract) {
    var from_til = CallInfo.file_info.partners[partner].contracts[contract].start_date;
    from_til +=  " ~ ";
    var aux = CallInfo.file_info.partners[partner].contracts[contract].end_date;
    if (aux == "") {
        from_til += "ND"
    }
    else {
        from_til += aux;
    }
    var cups = CallInfo.file_info.partners[partner].contracts[contract].cups;
    var power = CallInfo.file_info.partners[partner].contracts[contract].power;

    return m(ListTile, {
        title: cups,
        subtitle: "Data: " + from_til,
        highSubtitle: "Potència: " + power,
        front: m(Icon, getIcon()),
        style: {
          color: "#502300",
          backgroundColor: "#F6F6F6"
        }
    });
}


CallInfo.showContracts = function(partner){
    var contract = 0;
    var aux = ["ini"];
    try{
      var numOfContracts = CallInfo.file_info.partners[partner].contracts.length;
    }
    catch(error) {
        aux[0] = "No hi ha contractes.";
    }

    if(aux[0]==="ini"){
        for (contract; contract < numOfContracts; contract++) {
            aux[contract] = CallInfo.contractInfo(partner, contract);
        }
    }

    Dialog.show(function() { return {
        title: 'Contractes:',
        backdrop: true,
        body: [
            m(List, {
              tiles: [
                aux,
              ],
            }),
        ],
        footerButtons: [
            m(Button, {
                label: "Tanca",
                events: {
                    onclick: function() {
                        Dialog.hide({id:'contracts'});
                    },
                },
            }),
        ],
        didHide: function() {m.redraw();}
    };},{id:'contracts'});
}


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
            m("center",
                m("div", CallInfo.infoPhone())
            ),
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
