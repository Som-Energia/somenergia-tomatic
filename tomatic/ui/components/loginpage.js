
module.exports = function() {

var m = require('mithril');
var Button = require('polythene-mithril-button').Button;
var Card = require('polythene-mithril-card').Card;
var Auth = require('./auth')
require('./loginpage.styl')

var SimpleCard = function(args) {
    return m(Card, {
        content: [
            {
                header: {
                    title: args.title,
                },
            },
            {
                text: {
                    content: args.content
                },
            },
            {
                actions: {
                    content: [
                        m('.flex'),
                        m(Button, {
                            label: args.button,
                            events: {
                                onclick: args.action,
                            },
                        })
                    ],
                },
            },
        ]
    });
};

var LoginPage = {
    view: function() {
        return m('.loginpage',
            m('.loginbox',
                SimpleCard({
                    title: "Es requereix identificació",
                    content: "Cal que us identifiqueu a Can Google amb l'usuari de Som Energia.",
                    button: 'Som-hi!',
                    action: function() {
                        Auth.authenticate()
                    },
                })
            )
        );
    },
};

return LoginPage;

}();

// vim: et ts=4 sw=4
