
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');
var getCookie = require('./utils').getCookie;

var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var List = require ('polythene-mithril-list').List;
var Ripple = require('polythene-mithril-ripple').Ripple;

var styleLogin = require('./callinfo_style.styl');
var Tomatic = require('./tomatic');

var Login = {};
var tomaticCookie = "tomaticCookie"

var previousLogin = null; // To detect login changes


Login.loginWatchTimer = 0;
Login.watchLoginChanges = function() {
	clearTimeout(Login.loginWatchTimer);
    var cookie = whoAreYou();
    var user = cookie.split(":")[0];
	if (user !== previousLogin) {
		console.log("Detected login change",previousLogin,"->",user);
		previousLogin = user;
		Login.onUserChanged.map(function(callback) {
			callback();
		})
		m.redraw();
	}
	Login.loginWatchTimer = setTimeout(
		Login.watchLoginChanges, 500);
}

Login.onLogout = [];
Login.onLogin = [];
Login.onUserChanged = [];

Login.logout = function() {
    document.cookie = tomaticCookie + "=; expires = Thu, 01 Jan 1970 00:00:00 GMT;SameSite=Strict;path=/"
    Login.onLogout.map(function(callback) {
        callback();
    })
}

Date.prototype.addHours = function(h) {
   this.setTime(this.getTime() + (h*60*60*1000));
   return this;
}

Login.myName = function() {
    var cookie = whoAreYou();
    var user = cookie.split(":")[0];
    return user;
}

Login.currentExtension = function() {
    var cookie_value = getCookie(tomaticCookie);
    if (cookie_value === ":") return -1;
    var extension = cookie_value.split(":")[1].toString();
    return extension === "" ? -1 : extension;
}


var setCookieInfo = function(vnode){
    var name_button = vnode.target.innerText;
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
        document.cookie = tomaticCookie + "=" + value + ";" + expires + ";SameSite=Strict;path=/";
    }
    Login.onLogin.map(function(callback) {
        callback();
    })
}


var listOfPersons = function() {
    var aux = [];
    var persons = Tomatic.persons().extensions;

    for (id in persons){
        var name = Tomatic.formatName(id);
        var color = "#" + Tomatic.persons().colors[id];
		if (name == '-') {
            continue;
        }
        else if (name == '>>>CONTESTADOR<<<'){
            continue;
        }
        aux.push(m(Button, {
            id: id,
            className: 'btn-list',
            label: name,
            border: true,
            style: { backgroundColor: color },
            events: {
                onclick: function(id) {
                    setCookieInfo(id);
                    Dialog.hide({id:'whoAreYou'});
                },
            },
        }));
    }
    return m(List, { tiles:aux, className:'list-users' });
}


Login.askWhoAreYou = function() {
    Dialog.show(function() { return {
        className: 'dialog-login',
        title: 'Qui ets?',
        backdrop: true,
        body: [
            listOfPersons()
        ],
        footerButtons: [
            m(Button, {
                label: "Cancel·la",
                events: {
                    onclick: function() {
                        Dialog.hide({id:'whoAreYou'});
                    },
                },
            }),
        ],
        didHide: function() {m.redraw();}
    };},{id:'whoAreYou'});
}

var whoAreYou = function() {
    var cookie = getCookie(tomaticCookie);
    return (cookie === "" ? ":" : cookie);
}

var exitIcon = function(){
    return m(".icon-exit", [
        m("i.fas.fa-times-circle"),
    ]);
}

Login.identification = function() {
    var info = whoAreYou();
    var nom = "IDENTIFICAR";
    var color = 'rgba(255, 255, 255, 0.7)';

    if (info !== ":") {
        var aux = info.split(":");
        var id = aux[0];
        nom = Tomatic.formatName(id);
        color = "#" + aux[2];
    }

    return m('.login-buttons', [
        m(Button, {
            className: 'btn-iden',
            label: nom,
            border: true,
            events: {
                onclick: function() {
                    Login.askWhoAreYou();
                },
            },
            style: { backgroundColor: color },
        }, m(Ripple)),
        m(Button, {
            className: 'btn-disconnect',
            label: exitIcon(),
            events: {
                onclick: Login.logout,
            },
        }, m(Ripple)),
    ]);
}

Login.watchLoginChanges();

return Login;

}();

// vim: noet ts=4 sw=4