var m = require('mithril')
var Doc = require('./doc').default
var Persons = require('./persons')
var Tomatic = require('../../services/tomatic')

const PersonsPage = {
  view: function () {
    return m('', [
      Doc(
        'Permet modificar la configuració personal de cadascú: ' +
          'Color, taula, extensió, indisponibilitats...',
      ),
      Persons(Tomatic.persons().extensions),
    ])
  },
}
module.exports = PersonsPage

// vim: et ts=2 sw=2
