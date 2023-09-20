// Busy list editor
import m from 'mithril'

import { Dialog } from 'polythene-mithril-dialog'
import { Button } from 'polythene-mithril-button'
import { List } from 'polythene-mithril-list'
import { ListTile } from 'polythene-mithril-list-tile'
import { TextField } from 'polythene-mithril-textfield'
import { RadioGroup } from 'polythene-mithril-radio-group'
import { IconButton } from 'polythene-mithril-icon-button'
import { Checkbox } from 'polythene-mithril-checkbox'
import Select from './select'
import Labeled from './labeled'
import Tomatic from '../../services/tomatic'
import iconPlus from 'mmsvg/templarian/msvg/plus'
import iconDelete from 'mmsvg/google/msvg/action/delete'

function nextMonday(date) {
  var d = date || new Date()
  d.setDate(d.getDate() + 14 - ((6 + d.getDay()) % 7))
  return d.toISOString().substr(0, 10)
}

var BusyList = {
  view: function (vnode, attrs) {
    return m('', [
      m(List, {
        header: {
          title: m('.layout.justified.center', [
            vnode.attrs.title,
            m(IconButton, {
              icon: { svg: iconPlus },
              compact: true,
              wash: true,
              class: 'colored',
              events: {
                onclick: function () {
                  var newEntry = {
                    weekday: vnode.attrs.isOneShot ? undefined : '',
                    date: vnode.attrs.isOneShot ? nextMonday() : undefined,
                    reason: '',
                    optional: true,
                    turns: '0000',
                  }
                  editAvailability(newEntry, function (entry) {
                    vnode.attrs.entries.push(entry)
                    vnode.attrs.onChange && vnode.attrs.onChange()
                  })
                },
              },
            }),
          ]),
        },
        //compact: true,
        tiles: vnode.attrs.entries.map(function (entry, index) {
          var turns = Array.from(entry.turns).map(function (e) {
            return m.trust(e - 0 ? '&#x2612;' : '&#x2610;')
          })
          var day =
            entry.date || Tomatic.weekday(entry.weekday, 'Tots els dies')

          return m(ListTile, {
            front: m('.optionallabel', entry.optional ? 'Opcional' : ''),
            title: m('.layout.justified', [day, m('.turns', turns)]),
            subtitle: entry.reason,
            secondary: {
              content: m(IconButton, {
                icon: { svg: iconDelete },
                compact: true,
                wash: true,
                class: 'colored',
                events: {
                  onclick: function () {
                    vnode.attrs.entries.splice(index, 1)
                    vnode.attrs.onChange && vnode.attrs.onChange()
                  },
                },
              }),
            },
            events: {
              onclick: function () {
                editAvailability(entry, function (modifiedEntry) {
                  Object.assign(entry, modifiedEntry)
                  vnode.attrs.onChange && vnode.attrs.onChange()
                })
              },
            },
          })
        }),
        borders: true,
        hoverable: true,
      }),
    ])
  },
}

var BusyEntryEditor = {
  oncreate: function (vnode) {
    // Focus on the first enabled input
    // Note: if done without the setTimeout, styles are not applied
    setTimeout(function () {
      vnode.dom.querySelector('input:enabled').focus()
      m.redraw()
    }, 0)
  },
  oninit: function (vnode) {
    vnode.state.busy = vnode.attrs.busy
  },
  view: function (vnode) {
    var busy = vnode.attrs.busy
    return m('.busyentryeditor', [
      m(TextField, {
        label: 'Motiu',
        floatingLabel: true,
        help: 'Explica el motiu, com a referència',
        autofocus: true,
        required: true,
        value: busy.reason,
        onChange: function (state) {
          busy.reason = state.value
        },
      }),
      m(
        Labeled,
        {
          label: 'Opcional?',
          help: 'Es pot descartar si estem apurats?',
          id: 'optional',
        },
        m(RadioGroup, {
          name: 'optional',
          id: 'optional',
          onChange: function (state) {
            busy.optional = state.value === 'y'
          },
          className: 'layout.pe-textfield__input',
          all: {
            className: 'flex',
          },
          buttons: [
            {
              label: 'Sí',
              value: 'y',
              checked: busy.optional,
            },
            {
              label: 'No',
              value: 'n',
              checked: !busy.optional,
            },
          ],
        }),
      ),
      busy.weekday !== undefined
        ? m(Select, {
            label: 'Dia de la setmana',
            value: busy.weekday,
            options: {
              '': 'Tots els dies',
              dl: 'Dilluns',
              dm: 'Dimarts',
              dx: 'Dimecres',
              dj: 'Dijous',
              dv: 'Divendres',
            },
            onChange: function (ev) {
              busy.weekday = ev.target.value
            },
          })
        : [],
      busy.weekday === undefined
        ? [
            m(
              Labeled,
              { label: 'Data' },
              m(TextField, {
                type: 'date',
                required: true,
                value: busy.date,
                onChange: function (ev) {
                  busy.date = ev.value
                },
              }),
            ),
          ]
        : [],
      m(
        Labeled,
        { label: 'Marca les hores que no estaràs disponible:' },
        Array.from(busy.turns).map(function (active, i) {
          var hours = Tomatic.grid().hours
          return m(
            '',
            m(Checkbox, {
              label: hours[i] + ' - ' + hours[i + 1],
              checked: active === '1',
              onChange: function (state) {
                busy.turns =
                  busy.turns.substr(0, i) +
                  (busy.turns[i] === '1' ? '0' : '1') +
                  busy.turns.substr(i + 1)
              },
            }),
          )
        }),
      ),
    ])
  },
}

var editAvailability = function (receivedData, updateCallback) {
  var busy = Object.assign({}, receivedData)
  Dialog.show(
    function () {
      return {
        id: 'BusyEditor',
        title: 'Edita indisponibilitat',
        backdrop: true,
        body: m(BusyEntryEditor, {
          busy: busy,
        }),
        footerButtons: [
          m(Button, {
            label: 'Accepta',
            events: {
              onclick: function () {
                updateCallback(busy)
                Dialog.hide({ id: 'BusyEditor' })
              },
            },
            disabled:
              !busy.reason ||
              (busy.weekday === undefined && !busy.date) ||
              busy.turns === '0000',
          }),
          m(Button, {
            label: 'Cancel·la',
            events: {
              onclick: function () {
                Dialog.hide({ id: 'BusyEditor' })
              },
            },
          }),
        ],
      }
    },
    { id: 'BusyEditor' },
  )
}

var editAvailabilities = function (name) {
  Tomatic.retrieveBusyData(name, function (data) {
    Dialog.show(
      function () {
        return {
          id: 'BusyListEditor',
          title: 'Edita indisponibilitats ' + Tomatic.formatName(name),
          backdrop: true,
          body: [
            m('.busylist', [
              m(BusyList, {
                title: 'Setmanals',
                entries: data.weekly,
                isOneShot: false,
                onChange: function () {
                  Tomatic.sendBusyData(name, data)
                },
              }),
              m(BusyList, {
                title: 'Puntuals',
                entries: data.oneshot,
                isOneShot: true,
                onChange: function () {
                  Tomatic.sendBusyData(name, data)
                },
              }),
            ]),
          ],
          footerButtons: [
            m(Button, {
              label: 'Tanca',
              events: {
                onclick: function () {
                  Dialog.hide({ id: 'BusyListEditor' })
                },
              },
            }),
          ],
        }
      },
      { id: 'BusyListEditor' },
    )
    //m.redraw();
  })
}

export default editAvailabilities

// vim: et sw=2 ts=2
