
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var Textfield = require('polythene-mithril-textfield').TextField;
var Card = require('polythene-mithril-card').Card;
// var List = require('polythene-mithril-ListTitle').ListTitle;


var CallInfo = {};

CallInfo.file_info = {};


CallInfo.getNumber = function(name) {
    var data = 0;

    Dialog.show(function() { return {
        title: 'Entra el número:',
        backdrop: true,
        body: [
            m(Textfield, {
                label: 'número',
                required: true,
                help: "Entra el número de telèfon",
                focusHelp: true,
                type: 'number',
                pattern: '[0-9]{9}$',
                onChange: function(state) {
                    data = state.value;
                }
            }),
        ],
        footerButtons: [
            m(Button, {
                label: "Fet!",
                events: {
                    onclick: function() {
                        if(data!==""){
                            CallInfo.file_info = { 1: "empty" }
                            CallInfo.getInfo(name, data);
                            Dialog.hide({id: 'whatPhone'});
                        }
                    },
                },
            }),
            m(Button, {
                label: "Cancel·la",
                events: {
                    onclick: function() {
                        CallInfo.file_info = {}
                        Dialog.hide({id:'whatPhone'});
                    },
                },
            }),
        ],
        didHide: function() {m.redraw();}
    };},{id:'whatPhone'});
};


CallInfo.getInfo = function (name, data) {
    
    if (name===undefined) {
        name = data; // es el phone
    }
    m.request({
        method: 'GET',
        url: '/api/info/'+name,
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

// TODO
CallInfo.generateGraphics = function(partner) {
    // gestio amb la info del partner per generar imatge
    return m("img", { src: "img/large.png", style: { maxWidth: "360px" } })
}


CallInfo.showContracts = function(partner){
    Dialog.show(function() { return {
        title: 'Contractes:',
        backdrop: true,
        body: [
            m(Textfield, {
                label: 'número',
                required: true,
                help: "Entra el número de telèfon",
                focusHelp: true,
                type: 'number',
                pattern: '[0-9]{9}$',
                onChange: function(state) {
                    data = state.value;
                }
            }),
        ],
        footerButtons: [
            m(Button, {
                label: "Fet!",
                events: {
                    onclick: function() {
                        if(data!==""){
                            CallInfo.file_info = { 1: "empty" }
                            CallInfo.getInfo(name, data);
                            Dialog.hide({id: 'whatPhone'});
                        }
                    },
                },
            }),
            m(Button, {
                label: "Cancel·la",
                events: {
                    onclick: function() {
                        CallInfo.file_info = {}
                        Dialog.hide({id:'whatPhone'});
                    },
                },
            }),
        ],
        didHide: function() {m.redraw();}
    };},{id:'whatPhone'});
}


// Mirar com fer-ho sense això
function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}


// TODO
function getIcon() {
    // Mirem estat del client
    var image = "img/avatar.png";
    return {size: "large", avatar: "true", src: image};
}


CallInfo.allInfo = function (name) {
    var partner = 0;
    var numOfPartners = CallInfo.file_info.partners.length;
    var style = {
        maxWidth: "500px",
        backgroundColor: "#FFFFFF"
    }
    var header = {
        title: CallInfo.file_info.partners[partner].name, 
        subtitle: CallInfo.file_info.partners[partner].id_soci, 
        icon: getIcon(),
    };
    var media = { // Grafica interessant generada a partir de la info
        content: CallInfo.generateGraphics(partner),
    }
    var primary = {
        title: CallInfo.file_info.partners[partner].lang,
        subtitle: CallInfo.file_info.partners[partner].email,
    };
    return m(Card, {
            style: style,
            content: [
                { header: header },
                { media: media },
                { primary: primary },
                { actions: {
                    content: [
                        m(Button, { // Centrar
                            label: "More"
                            events: {
                                onclick: function() {
                                    CallInfo.showContracts(partner);
                                },
                            },
                        }),
                    ]
                } },
                {
                  text: {
                    content: CallInfo.file_info.partners[partner].city,
                  }
                }
            ]
        });
}


CallInfo.infoPhone = function (name) {
    
    if (isEmpty(CallInfo.file_info)) {
        return m("body", 'No hi ha informació.')
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m("body", 'Cercant informació.')
    } else {
        return m('', CallInfo.allInfo());
    }
};


CallInfo.mainPage = function(name) {
    return m("center", [
            m("h2", {class: "title"}, 'Info:'),
            m(Button, {
                label: "Get Number!",
                events: {
                    onclick: function() {
                        var current = CallInfo.getNumber();

                    },
                },
            }),
            m('center', CallInfo.infoPhone()),
    ]);
}


return CallInfo;


}();


// vim: noet ts=4 sw=4
