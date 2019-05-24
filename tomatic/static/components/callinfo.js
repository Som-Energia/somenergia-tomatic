
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
var id = "";
var reason = [];
var reasons = [];
var log = [];

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
            reasons=response.info.info;
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


var saveLogCalls = function(msg) {
    m.request({
        method: 'POST',
        url: '/api/reasons/'+CallInfo.phone,
        data: msg,
        deserialize: jsyaml.load,
    }).then(function(response){
        console.debug("Info POST Response: ",response);
        if (response.info.message !== "ok" ) {
            console.debug("Error al fer log dels motius: ", response.info.message)
        }
    }, function(error) {
        console.debug('Info POST apicall failed: ', error);
    });
}


function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}


var llistaMotius = function() {
    var aux = [];
    for(var i = 0; i<reasons.length; i++) {
        aux[i] = m(ListTile, {
            style: { fontSize: '14px' },
            selectable: 'true',
            ink: 'true',
            ripple: {
              opacityDecayVelocity: '0.5',
            },
            title: reasons[i],
            secondary: {
                content: m(Checkbox, {
                    defautCheked: false,
                    value: '100',
                    style: { color: "#ff9800" },
                    onChange: newState => {
                        var r = newState.event.path[5].textContent;
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
    return m("div", {class:'motius'}, m(List, {tiles: aux}));
}


var motiu = function() {
    var text = {
        content: m('', [ llistaMotius() ])
    };
    var save = m(Button, {
        label: "Desa",
        events: {
            onclick: function() {
                var message = (id === "" ? "Unknown" : id)
                var time = new Date();
                time.getTime();
                message += (' ('+time.toString().slice(0,21)+'): ')
                for(var i=0; i<reason.length; i++){
                    message += (reason[i])
                    if (i < reason.length-1) {
                        message += ', '
                    }
                }
                saveLogCalls(message);
            },
        },
        border: 'true',
    }, m(Ripple));

    return m(Card, {
        class: 'card-motius',
        content: [
            { primary: { 
                title: 'Motiu:', 
                subtitle: 'Selecciona la raó de la trucada'
            } },
            { text: text  },
            { actions: { content: save } }
        ]
    });
}


var llistaLog = function() {
    var aux = [];
    for(var i = 0; i<log.length; i++) {
        aux[i] = m(ListTile, {
            style: { fontSize: '14px' },
            selectable: 'true',
            ink: 'true',
            ripple: {
              opacityDecayVelocity: '0.5',
            },
            title: log[i].split("\"")[1],
        });
    }
    if (log.length === 0) {
        aux[0] = m(ListTile, {
            style: { fontSize: '14px' },
            title: "No hi ha cap registre", 
        });
    }
    return m("div", {class:'logs'}, m(List, {tiles: aux}));
}


var logCalls = function() {
    var text = {
        content: m('', [ llistaLog() ])
    };
    return m(Card, {
        class: 'card-log',
        content: [
            { primary: { title: 'Històric:' } },
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
