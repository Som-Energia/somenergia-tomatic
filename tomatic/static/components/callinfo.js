
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
var Checkbox = require('polythene-mithril-checkbox').Checkbox;

var Proves = require('./proves');
var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

CallInfo.file_info = {};
CallInfo.phone = "";
var reason = [];
var reasons = {};
var log = [];
var desar = "Desa";
var reason_filter = ""
var extra = ""
var refresh = true
var calling_phone = ""

var getInfo = function () {
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


CallInfo.getReasons = function () {
    m.request({
        method: 'GET',
        url: '/api/reasons',
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al obtenir els motius: ", response.info.message)
        }
        else{
            aux = response.info.info;
            for (var i=0; i<aux.length; i++) {
                reasons[aux[i][0]] = false;
            }
        }
    }, function(error) {
        console.debug('Info GET apicall failed: ', error);
    });
};
CallInfo.getReasons();


var getLog = function () {
    m.request({
        method: 'GET',
        url: '/api/log/'+CallInfo.phone,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al obtenir els motius: ", response.info.message)
        }
        else{
            log=response.info.info;
        }
    }, function(error) {
        console.debug('Info GET apicall failed: ', error);
    });
};


var saveLogCalls = function(info) {
    desar = 'Desant';
    m.request({
        method: 'POST',
        url: '/api/reasons/'+CallInfo.phone,
        data: info,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info POST Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al fer log dels motius: ", response.info.message)
        }
        else {
            desar='Desa';
            getLog();

        }
    }, function(error) {
        console.debug('Info POST apicall failed: ', error);
    });
}

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

function conte(value) {
    return value.toLowerCase().includes(reason_filter.toLowerCase());
}

var selectReason = function(r) {
    reasons[r] = !reasons[r]

    var index = reason.indexOf(r);
    if (index > -1) {
        reason.splice(index, 1);
    }
    else {
        reason.push(r);
    }
}

var llistaMotius = function() {
    var aux = [];
    var list_reasons = Object.keys(reasons);
    if (reason_filter !== "") {
        var filtered = list_reasons.filter(reason => conte(reason));
    }
    else {
        var filtered = list_reasons;
    }
    for(var i = 0; i<filtered.length; i++) {
        aux[i] = m(ListTile, {
            class: "llista-motius",
            compact: true,
            selectable: true,
            ink: 'true',
            ripple: {
              opacityDecayVelocity: '0.5',
            },
            title: filtered[i],
            secondary: {
                content:
                m(Checkbox, {
                    class: "checkbox-motius",
                    name: 'checkbox',
                    checked: reasons[filtered[i]],
                    value: filtered[i],
                    onChange: newState => {
                        selectReason(newState.event.target.value)
                    }
                }),
            },
            events: {
                onclick: function(vnode) {
                    selectReason(vnode.srcElement.innerText);
                }
            },
        });
    }
    return m(".motius", m(List, {compact: true, tiles: aux}));
}


var date2str = function (x, y) {
    var z = {
        M: x.getMonth() + 1,
        d: x.getDate(),
        h: x.getHours(),
        m: x.getMinutes(),
        s: x.getSeconds()
    };
    y = y.replace(/(M+|d+|h+|m+|s+)/g, function(v) {
        return ((v.length > 1 ? "0" : "") + eval('z.' + v.slice(-1))).slice(-2)
    });

    return y.replace(/(y+)/g, function(v) {
        return x.getFullYear().toString().slice(-v.length)
    });
}


var motiu = function() {
    return m(Card, {
        class: 'card-motius',
        content: [
            { primary: { 
                title: m(".card-motius-title", [ 
                    m(".motiu", 'Motiu:'),
                    m(".filter", m(Textfield, {
                        class: "textfield-filter",
                        label: "Escriure per filtrar",
                        dense: true,
                        onChange: newValue => reason_filter = newValue.value,
                    })),
                    m(".save", m(Button, {
                        label: desar,
                        events: {
                            onclick: function() {
                                var person = document.cookie.split(":")[0]
                                var time = new Date();
                                time.getTime();
                                var moment = date2str(time, "dd-MM-yyyy hh:mm:ss")
                                console.log(extra)
                                for( i in reason) {
                                    saveLogCalls(moment +'¬'+person+'¬'+reason[i]+'¬'+extra);
                                    reasons[reason[i]] = false;
                                }
                                reason = []
                            },
                        },
                        border: 'true',
                        disabled: ((desar === "Desa" && document.cookie !== "") ? false : true),
                    }, m(Ripple))),
                ]),
            } },
            { text: {
                content: m("", [
                        llistaMotius(),
                        m(Textfield, {
                            class: "textfield-comentaris",
                            label: "Algun comentari?",
                            floatingLabel: true,
                            dense: true,
                            onChange: newValue => extra = newValue.value,
                            disabled: ((desar === "Desa" && document.cookie !== "") ? false : true),
                        }),
                    ])
                }
            },
        ]
    });
}


var llistaLog = function() {
    var aux = []
    for(var i = log.length-1; i>=0; i--) {
        var missatge = log[i][5]+" ("+log[i][0]+"): "+log[i][2];
        aux.push(m(ListTile, {
            class: "registres",
            compact: true,
            selectable: 'true',
            ink: 'true',
            ripple: {
              opacityDecayVelocity: '0.5',
            },
            title: missatge,
        }));
    }
    if (log.length === 0) {
        aux[0] = m(ListTile, {
            class: "registres",
            compact: true,
            title: "No hi ha cap registre",
        });
    }
    return m(".logs", m(List, {compact: true, tiles: aux}));
}


var logCalls = function() {
    return m(Card, {
        class: 'card-log',
        content: [
            { primary: { title: m(".title",'Històric:') } },
            { text: {
                content: llistaLog()
            }},
        ]
    });
}


var infoPhone = function () {
    if (isEmpty(CallInfo.file_info)) {
        return m('center', m("body", 'No hi ha informació.'));
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m('center',m(Spinner, { show: "true" } ));
    } else {
        return m("", [
            Proves.allInfo(CallInfo.file_info, CallInfo.phone),
            motiu(),
            logCalls(),
        ]);
    }
};


CallInfo.refreshInfo = function(phone) {
    if (phone == "") {
        CallInfo.file_info = {};
    }
    else if (refresh) {
        CallInfo.phone = phone;
        CallInfo.file_info = { 1: "empty" }
        Proves.main_partner = 0;
        getInfo();
        log = [];
        getLog();
    }
    else {
        calling_phone = phone;
    }
}


var lookForPhoneInfo = function() {
    if(CallInfo.phone!==0 && CallInfo.phone!==""){
        CallInfo.file_info = { 1: "empty" }
        Proves.main_partner = 0;
        getInfo();
        //reason = [];
        log = [];
        getLog();
    } 
    else {
         CallInfo.file_info = {}
    }
}

var bloquejarTrucada = function() {
    var block = m(Button, {
        label: (refresh ? "Block" : "Blocked"),
        events: {
            onclick: function() {
                refresh = !refresh
            },
        },
        border: 'true',
        style: {
            position: 'absolute',
            right: 0,
            marginRight: '40px',
            marginTop: '-15px',
        },
    }, m(Ripple));

    var refresh_button = m(Button, {
        label: 'R',
        events: {
            onclick: function() {
                refresh = true
                var num = calling_phone
                calling_phone = ""
                CallInfo.refreshInfo(num)
            },
        },
        border: 'true',
        disabled: calling_phone === "",
        style: {
            position: 'absolute',
            right: 0,
            marginRight: '10px',
            marginTop: '-15px',
        },
    }, m(Ripple));

    return m(Card, {
        class: 'num-entrant',
        content: [
            { primary: { 
                title: m("p", [
                    m("strong", "Número entrant: "),
                    CallInfo.phone,
                    block,
                    refresh_button,
                ]),
            } },
        ]
    });
}

var cercaInformacio = function() {
    return m(Card, {
        class: 'busca-info',
        content: [
            { primary: {
                title: m(".busca-info-title", [
                m(".label", "Número: "),
                m(Textfield, {
                    class: 'txtf-phone',
                    onChange: function(state) {
                        CallInfo.phone = state.value;
                    },
                    events: {
                        onkeypress: function(event){
                            uniCharCode(event)
                        }
                    },
                }),
                m(Button, {
                    class: 'btn-search',
                    label: "🔎",
                    events: {
                        onclick: function() {
                            lookForPhoneInfo();
                        },
                    }
                }, m(Ripple)),
            ]),
            } },
        ]
    });
}

function uniCharCode(event) {
    var char = event.which || event.keyCode;
    if (char === 13) {
        lookForPhoneInfo();
    }
}


CallInfo.mainPage = function() {
    return m( '', [
            m(".info", [
                cercaInformacio(),
                bloquejarTrucada(),
            ]),
            m("div", " "),
            m("div", infoPhone())
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
