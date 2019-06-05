
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
            style: { fontSize: '14px'},
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
                    name: 'checkbox',
                    checked: reasons[filtered[i]],
                    style: { color: "#ff9800" },
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
    return m("div", {class:'motius'}, m(List, {compact: true, tiles: aux}));
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
    var save = m(Button, {
        label: desar,
        events: {
            onclick: function() {
                var person = document.cookie.split(":")[0]
                var time = new Date();
                time.getTime();
                var moment = date2str(time, "dd-MM-yyyy hh:mm:ss")
                console.log(extra)
                for( i in reason) {
                    saveLogCalls(moment +'¬'+person+'¬'+reason[i]);
                    reasons[reason[i]] = false;
                }
                reason = []
            },
        },
        border: 'true',
        disabled: ((desar === "Desa" && document.cookie !== "") ? false : true),
    }, m(Ripple));

    var filter = m(Textfield, {
        label: "Escriure per filtrar",
        dense: true,
        style: { width: '400px', },
        onChange: newValue => reason_filter = newValue.value,
    });

    var observacions = m(Textfield, {
        label: "Algun comentari?",
        floatingLabel: true,
        dense: true,
        style: {marginTop: '-5px', width: '680px'},
        onChange: newValue => extra = newValue.value,
    });

    var text = {
        content: m('', [
            llistaMotius(),
            observacions,
        ])
    };

    return m(Card, {
        class: 'card-motius',
        content: [
            { primary: { 
                title: m("div",{style:{display: 'flex', alignItems: 'baseline'}}, [ 
                    m("b",{style:{marginTop: '5px'}}, 'Motiu:'),
                    m("p",{style:{marginLeft: '10px'}}, filter),
                    m("b", {style:{marginLeft: '80px'}}, save),
                ]),
                //subtitle: 'Selecciona la raó de la trucada'
            } },
            { text: text },
            //{ actions: { content: save } }
        ]
    });
}


var llistaLog = function() {
    var aux = []
    for(var i = log.length-1; i>=0; i--) {
        var missatge = log[i][5]+" ("+log[i][0]+"): "+log[i][2];
        aux.push(m(ListTile, {
            style: { fontSize: '14px' },
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
            style: { fontSize: '14px' },
            compact: true,
            title: "No hi ha cap registre",
        });
    }
    return m("div", {class:'logs'}, m(List, {compact: true, tiles: aux}));
}


var logCalls = function() {
    var text = {
        content: m('', [ llistaLog() ])
    };
    return m(Card, {
        class: 'card-log',
        content: [
            { primary: { title: m("b",'Històric:') } },
            { text: text  },
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


CallInfo.refreshInfo = function(phone,iden) {
    CallInfo.phone = phone;
    id = iden;
    if (phone == "") {
        CallInfo.file_info = {};
    }
    else {
        CallInfo.file_info = { 1: "empty" }
        Proves.main_partner = 0;
        getInfo();
        reason = [];
        log = [];
        getLog();
    }
}


CallInfo.mainPage = function() {
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
                                getInfo();
                                getLog();
                            } 
                            else {
                                 CallInfo.file_info = {}
                            }
                        },
                    }
                }, m(Ripple)),
            ]),
            m("div", " "),
            m("div", infoPhone())
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
