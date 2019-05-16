
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

var Proves = require('./proves');
var styleCallinfo = require('./callinfo_style.styl');

var CallInfo = {};

CallInfo.file_info = {};
CallInfo.phone = "";


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


function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}


CallInfo.infoPhone = function () {
    if (isEmpty(CallInfo.file_info)) {
        return m('center', m("body", 'No hi ha informació.'));
    }
    else if (CallInfo.file_info[1]==="empty"){
        return m('center',m(Spinner, { show: "true" } ));
    } else {
        return m('', Proves.allInfo(CallInfo.file_info));
    }
};


CallInfo.refreshInfo = function(phone) {
    CallInfo.phone = phone;
    if (phone == "") {
        CallInfo.file_info = {};
    }
    else {
        CallInfo.file_info[1] = "empty";
        Proves.main_partner = 0;
        CallInfo.getInfo();
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
                                CallInfo.getInfo();
                            } 
                            else {
                                 CallInfo.file_info = {}
                            }
                        },
                    }
                }, m(Ripple)),
            ]),
            m("div", " "),
            m("div", CallInfo.infoPhone())
    ]);
}

return CallInfo;

}();

// vim: noet ts=4 sw=4
