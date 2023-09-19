import m from 'mithril'
import { Card } from 'polythene-mithril-card'

var Doc = function (message) {
  return m(Card, {
    content: [
      {
        primary: {
          title: 'Info',
          subtitle: message,
        },
      },
    ],
  })
}

export default Doc

// vim: et ts=2 sw=2
