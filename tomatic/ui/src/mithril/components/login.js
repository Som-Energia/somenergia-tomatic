import m from 'mithril'
import { contrast } from './colorutils'
import { Button } from 'polythene-mithril-button'
import { Ripple } from 'polythene-mithril-ripple'
import './callinfo_style.styl'
import Tomatic from '../../services/tomatic'
import Auth from '../../services/auth'

var Login = {}

var exitIcon = function () {
  return m('.icon-exit', [m('i.fa.fa-sign-out-alt')])
}

Auth.onLogout.subscribe(() => m.route.set('/Login'))

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

export default Login

// vim: et ts=2 sw=2
