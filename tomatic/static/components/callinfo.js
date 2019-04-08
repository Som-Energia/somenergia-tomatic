
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

var CallInfo = {};

CallInfo.file_info = {};


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


CallInfo.showContract = function(partner, contract) {
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
            aux[contract] = CallInfo.showContract(partner, contract);
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
        name = data;
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


CallInfo.mainPage = function(name) {
    console.log(name);
    return m("center", [
            m("h2.title", 'Info:'),
            m(Button, {
                label: "Get Number!",
                events: {
                    onclick: function() {
                        var current = CallInfo.getNumber();

                    },
                },
            }),
            m("div", CallInfo.infoPhone()),
    ]);
}


return CallInfo;


}();


// vim: noet ts=4 sw=4
