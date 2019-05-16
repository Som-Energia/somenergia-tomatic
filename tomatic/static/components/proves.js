module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Ripple = require('polythene-mithril-ripple').Ripple;
var List = require ('polythene-mithril-list').List;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var Checkbox = require('polythene-mithril-checkbox').Checkbox;
var Card = require('polythene-mithril-card').Card;
var Button = require('polythene-mithril-button').Button;

var styleCallinfo = require('./callinfo_style.styl');

var Proves = {};

Proves.main_partner = 0;
var reason = [];
var reasons = ["prova1", "prova2", "prova3"];

var infoPartner = function(info){
    // var lang = info.lang;
    // var id = info.id_soci;
    return m("div", { 
        style: {
            marginTop: '10px',
            marginBottom: '10px'
        } },
        [
            m("", {style: {color: '#000'}} ,[
                m("b", info.name), 
                m("b",{style:{float: 'right', marginRight: '20px'}},"S | T")
            ]),
            m("", "DNI"),
            m("", info.state),
            m("", info.email),
            m("", "Ha obert OV?"),
            m("a", {"href":"url"}, "helpscout"),
        ]
    );
}


var contractCard = function(info) {
    var from_til = info.start_date + " ~ ";
    var aux = info.end_date;
    if (aux == "") {
        from_til += "ND"
    }
    else {
        from_til += aux;
    }
    return m("div", {
        style: {
            border: '2px solid #9aa000',
            marginLeft: '10px',
            marginRight: '10px',
            marginBottom: '10px',
            width: '515px',
        } },
        [
            m("div", { 
                style: {
                    marginTop: '5px',
                    marginLeft: '10px',
                    width: '500px',
                    marginBottom: '5px',
                    color: '#000'
                } },
                [
                    m("div", [
                        m("b", "Número: "),
                        m("b",{style:{float: 'right', marginRight: '20px'}}, from_til)
                    ]),
                    m("div", "CUPS: ", info.cups),
                    m("div", "Potència: ", info.power),
                    m("div", "Tarifa: ", info.fare),
                    m("div", "R Obertes ATR: "),
                    m("div", "Última data facturació: "),
                    m("div", "Facturació suspesa:"),
                    m("div", "Estat: ", info.state),
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
        style: {
            backgroundColor: '#EEEEEE',
            width: '540px',
            height: '450px',
            overflow: 'auto',
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
            aux2[1] = 'ORG';
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
        { 
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


var llistaMotius = function() {
    var aux = [];
    for(var i = 0; i<reasons.length; i++) {
        aux[i] = m(ListTile, {
            selectable: 'true',
            ink: 'true',
            ripple: {
              opacityDecayVelocity: '0.5',
            },
            subtitle: reasons[i],
            secondary: {
                content: m(Checkbox, {
                    value: '100',
                    style: { color: "#ff9800" },
                    onChange: state => {
                        var r = state.event.path[5].textContent;
                        var index = reason.indexOf(r);
                        if (index > -1) {
                           reason.splice(index, 1);
                        }
                        else {
                            reason.push(r);
                        }
                    },
                })
            },
        });
    }

    return m("div", {
        style: {
            backgroundColor: '#EEEEEE',
            width: '400px',
            height: '200px',
            overflow: 'auto',
        } },
        [
            m(List, {
                tiles: [ aux ],
            })
        ]
    );

    return 
}


var motiu = function() {
    var text = {
        content: m('', [
            llistaMotius()
            ])
    };
    return m(Card, {
        //class: 'card-contracts',
        style: {
            maxWidth: '470px',
            maxHeight: '400px',
            position: 'absolute',
            right: '0',
            marginRight: '40px',
            display: 'inline-block',
        },
        content: [
            { primary: { title: 'Motiu:', subtitle: 'Selecciona la raó de la trucada'} },
            { text: text  },
        ]
    });
}


Proves.allInfo = function(info) {
    return m("", [
        mainInfoCards(info),
        motiu(),
    ]);
}

return Proves;

}();