
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
var Spinner = require('polythene-mithril-material-design-spinner').MaterialDesignSpinner;
var Checkbox = require('polythene-mithril-checkbox').Checkbox;

var PartnerInfo = require('./partnerinfo');
var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};


CallInfo.file_info = {};
CallInfo.search = "";

var call_reasons = {};
var log_calls = [];

var call = {
    'phone': "",
    'date': "",
    'log_call_reasons': [],
    'reason': [],
    'extra': "",
};

var addr = "";
var desar = "Desa";
var reason_filter = ""
var refresh = true
var calling_phone = ""
var search_by = "phone"

var fillCallInfo = function(phone) {
    call['phone']=phone;
    var time= new Date();
    time.getTime();
    var moment=date2str(time, "dd-MM-yyyy hh:mm:ss");
    call['date']=moment;
}

var clearCallInfo = function() {
    call['phone']="";
    call['date']="";
    call['log_call_reasons']=[];
    call['reason']=[];
    call['extra']="";
}

var getInfo = function () {
    m.request({
        method: 'POST',
        url: '/api/info',
        data: search_by+"¬"+CallInfo.search,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            if(response.info.message === "Masses resultats.") {
                CallInfo.file_info = { 1: "toomuch" };
            }
            else {
                CallInfo.file_info = {}
            }
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
                call_reasons[aux[i][0]] = false;
            }
        }
    }, function(error) {
        console.debug('Info GET apicall failed: ', error);
    });
};
CallInfo.getReasons();

var getLog = function () {
    call["log_call_reasons"] = [];
    call["log_call_reasons"].push("lookingfor");
    m.request({
        method: 'GET',
        url: '/api/log/'+call['phone'],
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al obtenir els motius: ", response.info.message)
            call["log_call_reasons"] = [];
        }
        else{
            call['log_call_reasons']=response.info.info;
        }
    }, function(error) {
        console.debug('Info GET apicall failed: ', error);
        call["log_call_reasons"] = [];
    });
};

CallInfo.getLogPerson = function () {
    log_calls = [];
    log_calls.push("lookingfor");
    m.request({
        method: 'GET',
        url: '/api/personlog/'+document.cookie.split(":")[0],
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al obtenir el registre de trucades ateses: ", response.info.message)
            log_calls = [];
        }
        else{
            log_calls=response.info.info;
        }
    }, function(error) {
        log_calls = [];
        console.debug('Info GET apicall failed: ', error);
    });
};
if(document.cookie){
    CallInfo.getLogPerson();
}


var saveLogCalls = function(info) {
    desar = 'Desant';
    m.request({
        method: 'POST',
        url: '/api/reasons/'+call['phone'],
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
            CallInfo.getLogPerson();

        }
    }, function(error) {
        console.debug('Info POST apicall failed: ', error);
    });
}

var searchIcon = function(){
    return m(".icon-search",
    [
        m("script", {src: "https://kit.fontawesome.com/c81e1a5696.js"}),
        m("i", {class: "fas fa-search"}),
    ]);
}

var lockIcon = function(){
    return m(".icon-lock",
    [
        m("script", {src: "https://kit.fontawesome.com/c81e1a5696.js"}),
        m("i", {class: "fas fa-lock-open"}),
    ]);
}

var lockedIcon = function(){
    return m(".icon-lock",
    [
        m("script", {src: "https://kit.fontawesome.com/c81e1a5696.js"}),
        m("i", {class: "fas fa-lock"}),
    ]);
}

var newTabIcon = function(){
    return m(".icon-new-tab",
    [
        m("script", {src: "https://kit.fontawesome.com/c81e1a5696.js"}),
        m("i", {class: "fas fa-external-link-alt"}),
    ]);
}

var refreshIcon = function(){
    return m(".icon-refresh",
    [
        m("script", {src: "https://kit.fontawesome.com/c81e1a5696.js"}),
        m("i", {class: "fas fa-redo-alt"}),
    ]);
}

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

function conte(value) {
    return value.toLowerCase().includes(reason_filter.toLowerCase());
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

var selectReason = function(r) {
    call_reasons[r] = !call_reasons[r]

    var index = call['reason'].indexOf(r);
    if (index > -1) {
        call['reason'].splice(index, 1);
    }
    else {
        call['reason'].push(r);
    }
}

var llistaMotius = function() {
    var aux = [];
    var list_reasons = Object.keys(call_reasons);
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
                    checked: call_reasons[filtered[i]],
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
                                for( i in call['reason']) {
                                    saveLogCalls(call['date']+'¬'+person+'¬'+call['reason'][i]+'¬'+call['extra']);
                                    call_reasons[call['reason'][i]] = false;
                                }
                                call['reason'] = []
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
                            onChange: newValue => call['extra'] = newValue.value,
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
    for(var i = call['log_call_reasons'].length-1; i>=0; i--) {
        var missatge = call['log_call_reasons'][i][5]
                    +" ("+call['log_call_reasons'][i][0]
                    +"): "+call['log_call_reasons'][i][2];
        aux.push(m(ListTile, {
            class: "registres",
            compact: true,
            title: missatge,
        }));
    }
    if (call['log_call_reasons'].length === 0) {
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
                content: ( call['log_call_reasons'][0] === "lookingfor" ?
                    m('center',m(Spinner, { show: "true" } )) : llistaLog())
            }},
        ]
    });
}



var atencionsLog = function() {
    var aux = []
    for(var i = log_calls.length-1; i>=0; i--) {
        var data = log_calls[i][0].split(":")
        var missatge = "("+data[0]+":"+data[1]+"): "+log_calls[i][4];
        var resolt = log_calls[i][2]!="";
        if(resolt){
            missatge += (", "+log_calls[i][2]);
        }
        aux.push(m(ListTile, {
            class: (resolt ? "registres" : "registres-red"),
            compact: true,
            selectable: 'true',
            ink: 'true',
            ripple: {
              opacityDecayVelocity: '0.5',
            },
            title: missatge,
        }));
    }
    if (log_calls.length === 0) {
        aux[0] = m(ListTile, {
            class: "registres",
            compact: true,
            title: "Cap trucada al registre.",
        });
    }
    return m(".logs-person", m(List, {compact: true, tiles: aux}));
}


var logPerson = function() {
    return m(Card, {
        class: 'card-log-person',
        content: [
            { primary: { 
                title: m(".title", [
                    'Trucades ateses:',
                    m(Button, {
                        class: "refresh-button",
                        label: refreshIcon(),
                        events: {
                            onclick: function() {
                                CallInfo.getLogPerson();
                            },
                        },
                        border: 'true',
                        disabled: ((log_calls.length === 0 && document.cookie !== "") ? false : true),
                    }, m(Ripple)),
                ])
            } },
            { text: {
                content: (log_calls[0] === "lookingfor" ?
                    m('center',m(Spinner, { show: "true" } )) : atencionsLog())
            }},
        ]
    });
}

var infoPhone = function () {
    if (isEmpty(CallInfo.file_info)) {
        return m('.text-info', m("body", 'No hi ha informació.'));
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m('.spinner-info',m(Spinner, { show: "true" } ));
    }
    else if (CallInfo.file_info[1]==="toomuch"){
        return m('.text-info', m("body", 'Cerca poc específica, retorna masses resultats.'));
    }else {
        return m('.call-info', [
            m("",PartnerInfo.allInfo(CallInfo.file_info, call['phone'])),
            (call["phone"] === "" ? "" :
                m("", [
                    motiu(),
                    logCalls(),
                ])
            ),
        ]);
    }
};


CallInfo.refreshInfo = function(data) {
    if(addr === "") {
        addr = data;
    } else {
        if (data == "") {
            CallInfo.file_info = {};
            clearCallInfo();
            log_calls = [];
        }
        else if (refresh) {
            fillCallInfo(data);
            CallInfo.search = data;
            CallInfo.file_info = { 1: "empty" };
            PartnerInfo.main_partner = 0;
            search_by = "phone"
            getLog();
            getInfo();
        }
        else {
            calling_phone = data;
        }
    }
}


var lookForPhoneInfo = function() {
    clearCallInfo();
    if (CallInfo.search !== 0 && CallInfo.search !== ""){
        CallInfo.file_info = { 1: "empty" };
        PartnerInfo.main_partner = 0;
        getInfo();
    } 
    else {
         CallInfo.file_info = {}
    }
}

var bloquejarTrucada = function() {
    return m(Card, {
        class: 'num-entrant',
        content: [
            { primary: { 
                title: m(".text-info", [
                    m(".label-text", "Número: "),
                    m(".normal-text", call['phone']),
                    m(Button, {
                        class: 'btn-lock',
                        label: (refresh ? lockIcon() : lockedIcon()),
                        border: 'true',
                        events: {
                            onclick: function() {
                                refresh = !refresh
                                if(refresh === true && calling_phone !== ""){
                                    var num = calling_phone;
                                    calling_phone = "";
                                    CallInfo.refreshInfo(num);
                                }
                            },
                        },
                    }, m(Ripple)),
                    m(Button, {
                        class: "btn-new-tab",
                        label: newTabIcon(),
                        url: {
                            href: addr+'/#!/Trucada',
                            target:"_blank",
                        },
                        border: 'true',
                    }, m(Ripple)),
                ]),
            } },
        ]
    });
}

var typeOfSearch = function() {
    return m("select",
        {
            id: "search-by",
            class: ".select-search",
            onchange: function() {
                search_by = document.getElementById("search-by").value;
            },
        },
        [
            m("option", {"value":"phone"},
              "Telèfon"
            ),
            m("option", {"value":"name"},
              "Cognoms/Nom"
            ),
            m("option", {"value":"nif"},
              "NIF"
            ),
            m("option", {"value":"soci"},
              "Número Soci"
            ),
            m("option", {"value":"email"},
              "Email"
            ),
            m("option", {"value":"all"},
              "Tot"
            )
        ]
    );
}

var cercaInformacio = function() {
    return m(Card, {
        class: 'busca-info',
        content: [
            { primary: {
                title: m(".busca-info-title", [
                typeOfSearch(),
                m(".label", "Cercador: "),
                m(Textfield, {
                    class: 'txtf-phone',
                    onChange: function(state) {
                        CallInfo.search = state.value;
                    },
                    events: {
                        onkeypress: function(event){
                            uniCharCode(event)
                        }
                    },
                }),
                m(Button, {
                    class: 'btn-search',
                    label: searchIcon(),
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
            m(".all-info-call", [
                infoPhone(),
                logPerson(),
            ])
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
