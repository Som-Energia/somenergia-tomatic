// Persons
// Displays the list of persons

import m from 'mithril'

import { IconButton } from 'polythene-mithril-icon-button'
import iconDate from 'mmsvg/google/msvg/action/date-range'
import iconEdit from 'mmsvg/google/msvg/editor/mode-edit'
import Tomatic from '../../services/tomatic'
import editAvailabilities from './busyeditor'
import editPerson from './editperson'

var Persons = function (extensions) {
  return [
    m('.extensions', [
      Object.keys(extensions || {})
        .sort()
        .map(function (name) {
          return m(
            '.extension',
            {
              className: name,
              _onclick: function () {
                editPerson(name)
              },
            },
            [
              Tomatic.formatName(name),
              m('br'),
              Tomatic.persons().extensions[name],
              m('.tooltip', [
                m(IconButton, {
                  icon: { svg: iconDate },
                  compact: true,
                  wash: true,
                  className: 'colored',
                  events: {
                    onclick: function () {
                      editAvailabilities(name)
                    },
                  },
                }),
                m(IconButton, {
                  icon: { svg: iconEdit },
                  compact: true,
                  wash: true,
                  className: 'colored',
                  events: {
                    onclick: function () {
                      editPerson(name)
                    },
                  },
                }),
              ]),
            ],
          )
        }),
      m(
        '.extension.add',
        {
          onclick: function () {
            editPerson()
          },
        },
        ['nova', m('br'), 'persona'],
      ),
    ]),
  ]
}

export default Persons
// vim: et sw=2 ts=2
