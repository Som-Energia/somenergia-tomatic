module.exports = (function () {
  var m = require('mithril')
  var Button = require('polythene-mithril-button').Button
  var Card = require('polythene-mithril-card').Card
  var Auth = require('../../services/auth')
  require('./loginpage.styl')
  var tomaticAvatar = require('../../images/tomatic-avatar.png')

  var SimpleCard = function (args) {
    console.log(args)
    return m(Card, {
      content: [
        {
          primary: {
            title: args.title,
            media: {
              ratio: 'square',
              size: 'small',
              content: m('img', {
                src: tomaticAvatar,
              }),
            },
          },
        },
        {
          text: { content: args.error ? m('.red', 'Error: ', args.error) : '' },
        },
        {
          text: { content: args.content },
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
              }),
            ],
          },
        },
      ],
    })
  }

  var LoginPage = {
    view: function () {
      return m(
        '.loginpage',
        m(
          '.loginbox',
          SimpleCard({
            title: 'Es requereix identificació',
            error: Auth.error(),
            content:
              "Cal que us identifiqueu a Can Google amb l'usuari de Som Energia.",
            button: 'Ves-hi!',
            action: function () {
              Auth.authenticate()
            },
          }),
        ),
      )
    },
  }

  return LoginPage
})()

// vim: et ts=4 sw=4
