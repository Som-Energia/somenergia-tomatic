
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');

var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var List = require ('polythene-mithril-list').List;

var Tomatic = require('./tomatic');
var Login = {};

Login.first = 0;


Date.prototype.addHours = function(h) {
   this.setTime(this.getTime() + (h*60*60*1000));
   return this;
}

Login.disconnect = function(){
    document.cookie = "; expires = Thu, 01 Jan 1970 00:00:00 GMT;path=/";
}

Login.getName = function(id) {
    return Tomatic.formatName(id);
}

Login.getColor = function(id) {
    return Tomatic.persons().colors[id];
}

Login.getMyExt = function() {
    var x = document.cookie;
    var aux = x.split(":");
    var ext = aux[1].toString();
    return ext;
}

Login.setCookieInfo = function(vnode){
    var aux = vnode.attributes;
    var name_button = aux["0"].ownerElement.innerText;
    var persons = Tomatic.persons().extensions;
    var found = false;

    for(id in persons){
        var name = Tomatic.formatName(id);
        if(name.toUpperCase() == name_button) {
            found = true;
            break;
        }
    }

    if(found){
        var value = id + ":" + Tomatic.persons().extensions[id] + ":" + Tomatic.persons().colors[id];
        var exp = new Date().addHours(3);
        var expires = "expires="+ exp.toUTCString();
        document.cookie = value + ";" + expires + ";path=/";
    }
}


Login.listOfPersons = function() {
    var aux = [];
    var persons = Tomatic.persons().extensions;

    for(id in persons){
        var name = Tomatic.formatName(id);
        var color = "#" + Tomatic.persons().colors[id];
        if(name !== '-' && name !== '>CONTESTADOR<'){
            aux.push(m(Button, { 
                label: name,
                border: true,
                style: { backgroundColor: color, margin: '4px' },
                events: {
                    onclick: function() {
                        Login.setCookieInfo(this);
                        Dialog.hide({id:'whoAreYou'});
                    },
                },
            }));
        }
    }
    return m(List, { tiles:aux, style:{marginBottom:'10px'} });
}


Login.askWhoAreYou = function() {
    Dialog.show(function() { return {
        title: 'Qui ets?',
        backdrop: true,
        body: [
            Login.listOfPersons(),
        ],
        footerButtons: [
            m(Button, {
                label: "Cancel·la",
                style: { center: true },
                events: {
                    onclick: function() {
                        Dialog.hide({id:'whoAreYou'});
                    },
                },
            }),
        ],
        style: { background: "#FFFFFF", width: '750px', marginLeft: '-180px' },
        didHide: function() {m.redraw();}
    };},{id:'whoAreYou'});
}


Login.whoAreYou = function() {
    var info = ":";
    var x = document.cookie;
    if (x !== "") {
        info = x;
    }
    return info;
}


return Login;

}();

// vim: noet ts=4 sw=4
