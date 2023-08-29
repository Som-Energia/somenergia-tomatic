'use strict'

// Persons
// Displays the list of persons

module.exports = (function () {
  var m = require('mithril')
  var IconButton = require('polythene-mithril-icon-button').IconButton
  var iconDate = require('mmsvg/google/msvg/action/date-range')
  var iconEdit = require('mmsvg/google/msvg/editor/mode-edit')
  var Tomatic = require('../../services/tomatic')
  var editAvailabilities = require('./busyeditor')
  var editPerson = require('./editperson')

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

  return Persons
})()
// vim: noet sw=4 ts=4
