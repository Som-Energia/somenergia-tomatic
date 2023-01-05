
module.exports = function() {

var m = require('mithril');
var jsyaml = require('js-yaml');
var contrast = require('./colorutils').contrast;

var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var List = require ('polythene-mithril-list').List;
var Ripple = require('polythene-mithril-ripple').Ripple;

var styleLogin = require('./callinfo_style.styl');
var Tomatic = require('./tomatic');
var api = require('./api')

var Login = {};

var previousLogin = null; // To detect login changes


Login.loginWatchTimer = 0;
Login.watchLoginChanges = function() {
    clearTimeout(Login.loginWatchTimer);
    var user = Login.myName();
    if (user !== previousLogin) {
        console.log("Detected login change",previousLogin,"->",user);
        previousLogin = user;
        Login.login();
        Login.onUserChanged.map(function(callback) {
            callback();
        })
        //m.redraw();
    }
    Login.loginWatchTimer = setTimeout(
        Login.watchLoginChanges, 500);
}

Login.onLogout = [];
Login.onLogin = [];
Login.onUserChanged = [];

Login.logout = function() {
    api.clearToken();
    Login.onLogout.map(function(callback) {
        callback();
    })
}

// TODO: Call this!
Login.login = function(){
    Login.onLogin.map(function(callback) {
        callback();
    })
}

Login.myName = function() {
    return api.userinfo()?.username || '';
}


var exitIcon = function(){
    return m(".icon-exit", [
        m("i.fa.fa-sign-out-alt"),
    ]);
}

Login.identification = function() {
    var nom = "IDENTIFICAR";
    var color = 'rgba(255, 255, 255, 0.7)';
    var id = Login.myName();

    if (id !== '') {
        nom = Tomatic.formatName(id);
        if (Tomatic.persons().colors) {
            color = "#" + Tomatic.persons().colors[id];
        }
    }

    return m('.login-buttons', [
        m(Button, {
            className: 'btn-iden',
            label: nom,
            border: true,
            style: {
                backgroundColor: color,
                color: contrast(color),
            },
        }, m(Ripple)),
        m(Button, {
            title: "Log out",
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

// vim: et ts=4 sw=4
