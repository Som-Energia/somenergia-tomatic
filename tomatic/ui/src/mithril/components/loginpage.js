import m from 'mithril'
import { Button } from 'polythene-mithril-button'
import { Card } from 'polythene-mithril-card'
import Auth from '../../services/auth'
import './loginpage.styl'
import tomaticAvatar from '../../images/tomatic-avatar.png'

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

export default LoginPage

// vim: et ts=2 sw=2
