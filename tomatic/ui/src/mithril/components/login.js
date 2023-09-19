  var m = require('mithril')
  var jsyaml = require('js-yaml')
  var contrast = require('./colorutils').contrast

  var Button = require('polythene-mithril-button').Button
  var List = require('polythene-mithril-list').List
  var Ripple = require('polythene-mithril-ripple').Ripple

  var styleLogin = require('./callinfo_style.styl')
  var Tomatic = require('../../services/tomatic')
  var Auth = require('../../services/auth')

  var Login = {}

  var exitIcon = function () {
    return m('.icon-exit', [m('i.fa.fa-sign-out-alt')])
  }

  Auth.onLogout.push(() => m.route.set('/Login'))

  Login.identification = function () {
    var nom = "IDENTIFICA'T"
    var color = 'rgba(255, 255, 255, 0.7)'
    var id = Auth.username()

    if (id !== '') {
      nom = Tomatic.formatName(id)
      if (Tomatic.persons().colors) {
        color = '#' + Tomatic.persons().colors[id]
      }
    }

    return m('.login-buttons', [
      m(
        Button,
        {
          className: 'btn-iden',
          label: nom,
          border: true,
          style: {
            backgroundColor: color,
            color: contrast(color),
          },
          events: {
            onclick: Auth.authenticate,
          },
        },
        m(Ripple),
      ),
      id !== '' &&
        m(
          Button,
          {
            title: 'Log out',
            className: 'btn-disconnect',
            label: exitIcon(),
            events: {
              onclick: Auth.logout,
            },
          },
          m(Ripple),
        ),
    ])
  }

module.exports = Login

// vim: et ts=2 sw=2
