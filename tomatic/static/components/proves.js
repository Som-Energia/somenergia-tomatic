module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Ripple = require('polythene-mithril-ripple').Ripple;
var List = require ('polythene-mithril-list').List;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var Card = require('polythene-mithril-card').Card;
var Button = require('polythene-mithril-button').Button;

var styleProves = require('./proves_style.styl');

var Proves = {};

Proves.main_partner = 0;


var infoPartner = function(info){
    // var lang = info.lang;
    var url = "https://secure.helpscout.net/search/?query=" + info.email;
    var dni = (info.dni.slice(0,2) === 'ES' ? info.dni.slice(2) : info.dni)
    return m("div", { //class: 'partner-card' },
        style: {
            marginTop: '10px',
            marginBottom: '10px',
        } },
        [
            m("div", [
                m("b", {style: {color: '#000'}} , info.name), 
                m("b",{style:{float: 'right', marginRight: '20px'}}, info.id_soci),
            ]),
            m("", dni),
            m("", info.state),
            m("a", {"href":url, target:"_blank"}, info.email),
            m("", "Ha obert OV? ", (info.ov ? "Sí" : "No")),
        ]
    );
}


var contractCard = function(info) {
    var from_til = (info.start_date !== false ? info.start_date : "No especificat");
    var aux = info.end_date;
    var num = info.number
    var s_num = num+"";
    var last_invoiced = (info.last_invoiced != "" ? info.last_invoiced : "No especificada")
    while (s_num.length < 7) s_num = "0" + s_num;
    if (aux == "" && from_til !== "No especificat") {
        from_til += " ⇨ Actualitat"
    }
    else if (from_til !== "No especificat") {
        from_til += (" ⇨ " + aux);
    }
    return m("div", { //class: 'contract-card-main' },
        style: {
            border: '2px solid #9aa000',
            marginLeft: '10px',
            marginRight: '10px',
            marginBottom: '10px',
            width: '515px',
        } },
        [
            m("div", { 
                style: { //class: 'contract-card-son' },
                    marginTop: '5px',
                    marginLeft: '10px',
                    width: '500px',
                    marginBottom: '5px',
                    color: '#000'
                } },
                [
                    m("div", [
                        m("b", "Número: ", s_num),
                        m("b",{style:{float: 'right', marginRight: '20px'}}, from_til)
                    ]),
                    m("div", "CUPS: ", info.cups),
                    m("div", "Potència: ", info.power),
                    m("div", "Tarifa: ", info.fare),
                    m("div", "Data última lectura facturada: ", last_invoiced),
                    m("div", {style:{color: '#E1232C'}} ,(info.has_open_r1s ? "Casos ATR R1 oberts." : "")),
                    m("div", {style:{color: '#E1232C'}} ,(info.has_open_bs ? "Cas ATR B1 obert." : "")),
                    m("div", "Facturació suspesa: ", (info.suspended_invoicing ? "Sí" : "No")),
                    m("div", [
                        m("b", "Estat pendent: ", info.pending_state),
                        m("b",{style:{float: 'right', marginRight: '20px'}}, [
                            (info.is_titular ? "T " : ""),
                            (info.is_partner ? "S " : ""),
                            (info.is_payer ? "P " : ""),
                            (info.is_notifier ? "N " : ""),
                        ])
                    ]),
                ]
            )
        ]
    );
}


var contractsField = function(info){
    var contract = 0;
    var aux = ["ini"];
    try{
      var numOfContracts = info.length;
    }
    catch(error) {
        aux[0] = m("center","No hi ha contractes.");
    }
    if(aux[0]==="ini"){
        for (contract; contract < numOfContracts; contract++) {
            aux[contract] = contractCard(info[contract]);
        }
    }
    return m("div", {
        style: { //class: 'contract-field' },
            backgroundColor: '#EEEEEE',
            width: '540px',
            height: '450px',
            overflow: 'auto',
            borderRadius: '2%',
        } },
        [
            m(List, {
                tiles: [ aux ],
            })
        ]
    );
}


var buttons = function(info) {
    var partner = 0;
    var numOfPartners = info.length;
    var aux = [];
    for (partner; partner < numOfPartners; partner++) {
        var name = info[partner].name;
        var aux2 = name.split(',');
        if (!aux2[1]){
            aux2 = name.split(' ');
            aux2[1] = aux2[0];
        }
        aux[partner] = m(Button, {
            id: partner,
            label: aux2[1],
            events: {
                onclick: function() {
                    var id = this.attributes.id.value;
                    Proves.main_partner = id;
                },
            },
            border: 'true',
            style: {
                borderColor: '#9aa000'
            }
        }, m(Ripple));
    }
    return m(List, { tiles: [ aux ] });
}


var listOfPartners = function(partners, button) {
    var partner = 0;
    var numOfPartners = partners.length;
    var aux = [];

    for (partner; partner < numOfPartners; partner++) {
        aux[partner] = specificPartnerCard(partners[partner], button);
    }

    return m(List, {
      tiles: [ aux[Proves.main_partner] ],
    });
}


var specificPartnerCard = function(partner, button) {
    var text = {
        content: m('', [
            infoPartner(partner),
            contractsField(partner.contracts)
            ])
    };

    return m(Card, {
        class: 'card-contracts',
        style: {maxWidth: '570px'},
        content: [
            { text: text  },
            { actions: { content: button } }
        ]
    });
}


var mainInfoCards = function(info) {
    return m("div", 
        { //class: 'main-card' },
        style: {
            marginLeft: '30px',
            height: '680px',
            display: 'inline-block',
            marginRight: '10px'
        } }, 
        [
            listOfPartners(info.partners, buttons(info.partners))
        ]
    );
}


Proves.allInfo = function(info, phone) {
    return m("", {style:{display: 'inline-block',}}, [
        mainInfoCards(info),
    ]);
}

return Proves;

}();