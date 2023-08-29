var m = require('mithril')
var Card = require('polythene-mithril-card').Card

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

// vim: noet ts=4 sw=4
