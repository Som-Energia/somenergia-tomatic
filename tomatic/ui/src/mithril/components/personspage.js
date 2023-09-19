import m from 'mithril'
import Doc from './doc'
import Persons from './persons'
import Tomatic from '../../services/tomatic'

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

export default PersonsPage

// vim: et ts=2 sw=2
