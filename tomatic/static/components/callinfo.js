
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
    'partner': 0,
    'contract': "",
    'reason': [],
    'extra': "",
    'log_call_reasons': [],
    'registered': false,
    'proc': false,
    'improc': false,
};

var addr = ""
var desar = "Desa"
var reason_filter = ""
var refresh = true
var calling_phone = ""
var search_by = "phone"
var update = false

var fillCallInfo = function(phone, date) {
    call['phone']=phone;
    if (date === "") {
        var time= new Date();
        time.getTime();
        date=date2str(time, "dd-MM-yyyy hh:mm:ss");
        update = false;
    }
    call['date']=date;
}

var clearCallInfo = function() {
    if (call["phone"] !== "" && !call["registered"]) {
        saveCall(call["date"]);
    }
    call['phone']="";
    call['date']="";
    call['log_call_reasons']=[];
    for( i in call['reason']) {
        call_reasons[call['reason'][i]] = false;
    }
    call['reason']=[];
    call['extra']="";
    call['registered']=false;
    call['contract']="";
    call['partner']=0,
    call['proc']=false;
    call['improc']=false;
    desar = "Desa";
}

var getInfo = function () {
    var info = btoa(CallInfo.search)
    m.request({
        method: 'GET',
        url: '/api/info/'+search_by+"/"+info,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ", response);
        if (response.info.message !== "ok" ) {
            if(response.info.message === "response_too_long") {
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
        url: '/api/generalReasons',
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
    call["log_call_reasons"]=[];
    call["log_call_reasons"].push("lookingfor");
    m.request({
        method: 'GET',
        url: '/api/log/'+call['phone'],
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al obtenir els motius: ", response.info.message)
            call["log_call_reasons"]=[];
        }
        else{
            call['log_call_reasons']=response.info.info;
        }
    }, function(error) {
        console.debug('Info GET apicall failed: ', error);
        call["log_call_reasons"]=[];
    });
};

CallInfo.getLogPerson = function () {
    log_calls=[];
    log_calls.push("lookingfor");
    m.request({
        method: 'GET',
        url: '/api/personlog/'+document.cookie.split(":")[0],
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info GET Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al obtenir trucades ateses.", response.info.message)
            log_calls=[];
        }
        else{
            log_calls=response.info.info;
        }
    }, function(error) {
        log_calls=[];
        console.debug('Info GET apicall failed: ', error);
    });
};
if(document.cookie){
    CallInfo.getLogPerson();
}

var saveLogCalls = function(phone, person, reason) {
    desar = 'Desant';
    saveCall(call["date"]);
    info = {
        "date": call['date'],
        "phone": call['phone'],
        "person": person,
        "reason": reason,
        "extra": call['extra'],
        "partner": call['partner'],
        "contract": call['contract'],
        "procedente": (call["proc"] ? "x" : ""),
        "improcedente": (call["improc"] ? "x" : ""),
    }
    m.request({
        method: 'POST',
        url: '/api/reasons',
        data: info,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info POST Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al desar motius telefon: ", response.info.message)
        }
        else if (call['phone'] === phone) {
            desar='Desa';
            call['proc']=false;
            call['improc']=false;
            call['extra']="";
            reason_filter="";
        }
    }, function(error) {
        console.debug('Info POST apicall failed: ', error);
    });
}

var saveCall = function(date) {
    var has_to_save = desar === 'Desant'
    var person = document.cookie.split(":")[0]
    var data = PartnerInfo.getPartnerAndContract(CallInfo.file_info)
    var contract = data['contract']
    var s_contract = ""
    if(contract !== -1) {
        s_contract = contract+"";
        while (s_contract.length < 7) s_contract = "0" + s_contract
    }
    var partner = (data["partner"] === -1 ? "" : data['partner'])
    call['contract'] = s_contract
    call['partner'] = partner
    var reasons = ""
    var len = call['reason'].length
    if (len > 0){
        for (var i=0; i < len-1; i++) {
            reasons += call['reason'][i] + ", "
        }
        reasons += call['reason'][len-1]
    }
    var info = {
        'data': call['date'],
        'telefon': call['phone'],
        'partner': (has_to_save ? partner : ""),
        'contracte': (has_to_save ? s_contract : ""),
        'motius': (has_to_save ? reasons : ""),
    }
    m.request({
        method: 'POST',
        url: '/api/' + (update ? 'updatelog/' : 'mylog/') + person,
        data: info,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info POST Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al fer log dels motius: ", response.info.message)
        }
        else {
            if (date === call["date"]) {
                call["registered"] = true
            }
            if (document.cookie !== "") CallInfo.getLogPerson();
        }
    }, function(error) {
        console.debug('Info POST apicall failed: ', error);
    });
}

var searchIcon = function(){
    return m(".icon-search",
    [
        m("i", {class: "fas fa-search"}),
    ]);
}

var lockIcon = function(){
    return m(".icon-lock",
    [
        m("i", {class: "fas fa-lock-open"}),
    ]);
}

var lockedIcon = function(){
    return m(".icon-lock",
    [
        m("i", {class: "fas fa-lock"}),
    ]);
}

var newTabIcon = function(){
    return m(".icon-new-tab",
    [
        m("i", {class: "fas fa-external-link-alt"}),
    ]);
}

var refreshIcon = function(){
    return m(".icon-refresh",
    [
        m("i", {class: "fas fa-redo-alt"}),
    ]);
}

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
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
    function conte(value) {
        return value.toLowerCase().includes(reason_filter.toLowerCase());
    }

    var aux = [];
    var list_reasons = Object.keys(call_reasons);
    if (reason_filter !== "") {
        var filtered = list_reasons.filter(conte);
    }
    else {
        var filtered = list_reasons;
    }
    var disabled = desar === "Desant" || CallInfo.search === "";
    return m(".motius", m(List, {
        compact: true,
        tiles: filtered.map(function(reason) {
            return m(ListTile, {
                class: "llista-motius",
                compact: true,
                selectable: true,
                ink: 'true',
                ripple: {
                  opacityDecayVelocity: '0.5',
                },
                title: reason,
                secondary: {
                    content:
                    m(Checkbox, {
                        class: "checkbox-motius",
                        name: 'checkbox',
                        checked: call_reasons[reason],
                        value: reason,
                        onChange: function(newState) {
                            selectReason(newState.event.target.value)
                        },
                        disabled: disabled,
                    }),
                },
                events: {
                    onclick: function(ev) {
                        selectReason(ev.srcElement.innerText);
                    }
                },
                disabled: disabled,
            });
        }),
    }));
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
                        value: reason_filter,
                        dense: true,
                        onChange: function(params) {
                            reason_filter = params.value
                        }
                    })),
                    m(Checkbox, {
                        class: "checkbox-proc",
                        name: 'proc',
                        checked: (call["proc"] && PartnerInfo.contract !== -1),
                        label: "Procedente",
                        disabled: (PartnerInfo.contract === -1) || (desar === "Desant"),
                        onChange: function() {
                            call["proc"] = !call["proc"]
                            if (call["proc"] && call["improc"]){
                                call["improc"] = false
                            }
                        },
                    }),
                    m(Checkbox, {
                        class: "checkbox-improc",
                        name: 'improc',
                        checked: (call["improc"] && PartnerInfo.contract !== -1),
                        label: "Improcedente",
                        disabled: (PartnerInfo.contract === -1) || (desar === "Desant"),
                        onChange: function() {
                            call["improc"] = !call["improc"]
                            if(call["proc"] && call["improc"]) {
                                call["proc"] = false
                            }
                        },
                    }),
                ]),
            } },
            { text: {
                content: m("", [
                        llistaMotius(),
                        m(".final-motius", [
                            m(Textfield, {
                                class: "textfield-comentaris",
                                label: "Algun comentari?",
                                floatingLabel: true,
                                dense: true,
                                value: call['extra'],
                                onChange: function(params) {
                                    call['extra'] = params.value
                                },
                                disabled: (desar !== "Desa" || CallInfo.search === ""),
                            }),
                            m(".save", m(Button, {
                                label: desar,
                                events: {
                                    onclick: function() {
                                        var person = document.cookie.split(":")[0]
                                        for( i in call['reason']) {
                                            saveLogCalls(call['phone'], person, call['reason'][i]);
                                            call_reasons[call['reason'][i]] = false;
                                        }
                                        call['reason']=[]
                                    },
                                },
                                border: 'true',
                                disabled: (desar !== "Desa" || CallInfo.search === ""),
                            }, m(Ripple))),
                        ]),
                    ])
                }
            },
        ]
    });
}

var llistaLog = function() {
    var aux = []
    for(var i = call['log_call_reasons'].length-1; i>=0; i--) {
        var missatge = call['log_call_reasons'][i][1]
                    +" ("+call['log_call_reasons'][i][0]
                    +"): "+call['log_call_reasons'][i][5];
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
    var mida = log_calls.length-1
    for(var i = mida; i>=0; i--) {
        var data = log_calls[i]["data"]
        var missatge = "("+ data +"): " + (log_calls[i]["telefon"] !== "" ?
            log_calls[i]["telefon"] : "Cercat");
        var resolt = log_calls[i]["motius"]!="";
        if (resolt) {
            missatge+=", "+ (log_calls[i]["partner"] == "" ?
                "Sense informació" : log_calls[i]["partner"])
            if (log_calls[i]["contracte"] !== "") {
                missatge += ", "+log_calls[i]["contracte"]
            }
            text = log_calls[i]["motius"]
            tipus = "tooltiptext"
            if(i===mida || i === mida-1) {
                tipus = "tooltiptext-first"
            }
            aux.push(m("div", {"class":"tooltip"}, [
                m(ListTile, {
                    class: "registres",
                    compact: true,
                    selectable: false,
                    title: missatge,
                    selected: call["date"] == missatge.split(')')[0].substr(1),
                }),
                m("span", {"class":tipus},
                  text
                )
            ]));
        }
        else {
            aux.push(m(ListTile, {
                class: "registres-red",
                compact: true,
                selectable: true,
                ink: true,
                ripple: {
                  opacityDecayVelocity: '0.5',
                },
                title: missatge,
                selected: call["date"] == missatge.split(')')[0].substr(1),
                events: {
                    onclick: function(ev) {
                        if (call["phone"] !== "" && !call["registered"]) {
                            saveCall(call["date"]);
                        }
                        update = true;
                        var info = ev.srcElement.innerText;
                        aux = info.toString().split(')');
                        var phone = aux[1].substr(2);
                        var date = aux[0].substr(1);
                        refreshCall(phone, date);
                    }
                },
            }));
        }
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
                        disabled: (log_calls.length !== 0 || document.cookie === ""),
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
        return m('.plane-info', m("body", 'No hi ha informació.'));
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m('.plane-info', m(Spinner, { show: "true" } ));
    }
    else if (CallInfo.file_info[1]==="toomuch"){
        return m('.plane-info', m("body", 'Cerca poc específica, retorna masses resultats.'));
    }else {
        return m('.call-info', [
            m('.plane-info',PartnerInfo.allInfo(CallInfo.file_info, call['phone'])),
        ]);
    }
};

var refreshCall = function(data, date) {
        clearCallInfo();
        fillCallInfo(data, date);
        CallInfo.search = data;
        CallInfo.file_info = { 1: "empty" };
        PartnerInfo.main_partner = 0;
        search_by = "phone"
        getLog();
        getInfo();
}

CallInfo.refreshInfo = function(data) {
    if(addr === "") {
        addr = data;
    }
    else if (data == "") {
        CallInfo.search = "";
        clearCallInfo();
        CallInfo.file_info = {};
        log_calls = [];
    }
    else if (refresh) {
        refreshCall(data, "");
    }
    else {
        calling_phone = data;
    }
}

var lookForPhoneInfo = function() {
    clearCallInfo();
    if (CallInfo.search !== 0 && CallInfo.search !== ""){
        fillCallInfo("", "");
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
            m("option", {"value":"phone"}, "Telèfon"),
            m("option", {"value":"name"}, "Cognoms/Nom"),
            m("option", {"value":"nif"}, "NIF"),
            m("option", {"value":"soci"}, "Número Soci"),
            m("option", {"value":"email"}, "Email"),
            m("option", {"value":"all"}, "Tot")
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
            m(".header-callinfo", [
                cercaInformacio(),
                bloquejarTrucada(),
            ]),
            m(".all-info-call", [
                infoPhone(),
                (document.cookie !== "" ? motiu() : ""),
                m("", [
                    logCalls(),
                    logPerson(),
                ])
            ])
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
