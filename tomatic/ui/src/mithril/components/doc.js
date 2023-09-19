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

module.exports = Doc

// vim: et ts=2 sw=2
