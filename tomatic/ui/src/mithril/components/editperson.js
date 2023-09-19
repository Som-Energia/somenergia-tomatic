// Persons
// Displays the list of persons

  var m = require('mithril')
  var Dialog = require('polythene-mithril-dialog').Dialog
  var TextField = require('polythene-mithril-textfield').TextField
  var Button = require('polythene-mithril-button').Button
  var Tomatic = require('../../services/tomatic')
  var Select = require('./select')
  var RgbEditor = require('./rgbeditor')

  var PersonEditor = {}
  PersonEditor.oncreate = function (vnode) {
    // Focus on the first enabled input
    // Note: if done without the setTimeout, styles are not applied
    setTimeout(function () {
      vnode.dom.querySelector('input:enabled').focus()
      m.redraw()
    }, 0)
  }
  PersonEditor.view = function (vnode) {
    vnode.state.name = vnode.attrs.name
    return m('.personEditor', [
      m(TextField, {
        label: 'Identificador',
        floatingLabel: true,
        pattern: '[a-z]{3,10}$',
        help: 'Identificador que es fa servir internament.',
        error: 'De 3 a 10 carácters. Només lletres en minúscules.',
        required: true,
        autofocus: vnode.attrs.newone,
        disabled: !vnode.attrs.newone,
        value: vnode.attrs.name || '',
        events: {
          oninput: function (ev) {
            ev.target.value = ev.target.value
              .toLowerCase()
              .replace(/[óòôö]/g, 'o')
              .replace(/[àáâä]/g, 'a')
              .replace(/[íìîï]/g, 'i')
              .replace(/[úûûü]/g, 'u')
              .replace(/[éèêë]/g, 'e')
              .replace(/[ç]/g, 'c')
              .replace(/[ñ]/g, 'n')
              .replace(/[^a-z]/g, '')
              .slice(0, 10)
          },
        },
        onChange: function (state) {
          vnode.attrs.name = state.value
        },
      }),
      m(TextField, {
        label: 'Nom mostrat',
        floatingLabel: true,
        autofocus: !vnode.attrs.newone,
        help: 'Nom amb accents, majúscules...',
        required: true,
        value: vnode.attrs.formatName,
        onChange: function (state) {
          vnode.attrs.formatName = state.value
        },
      }),
      m(TextField, {
        label: 'Correu electrònic',
        floatingLabel: true,
        type: 'email',
        help: 'Correu oficial que tens a Som Energia.',
        error: 'Correu invàlid.',
        required: true,
        value: vnode.attrs.email || '',
        onChange: function (state) {
          vnode.attrs.email = state.value
        },
      }),
      m(TextField, {
        label: 'Usuari ERP',
        floatingLabel: true,
        help: "Usuari amb el que entres a l'erp.",
        required: true,
        value: vnode.attrs.erpuser || '',
        onChange: function (state) {
          vnode.attrs.erpuser = state.value
        },
      }),
      m(TextField, {
        label: 'Extensio',
        type: 'number',
        pattern: '[0-9]{4}$',
        floatingLabel: true,
        help: 'Extensió de telèfon',
        required: true,
        value: vnode.attrs.extension,
        onChange: function (state) {
          vnode.attrs.extension = state.value
        },
      }),
      m(Select, {
        label: 'Taula',
        value: vnode.attrs.table,
        options: Object.keys(vnode.attrs.tables).reduce(
          function (d, k) {
            d[k] = vnode.attrs.tables[k]
            return d
          },
          { '-1': 'Sense taula' },
        ),
        onChange: function (ev) {
          vnode.attrs.table = ev.target.value
        },
      }),
      m(
        '.pe-textfield' +
          '.pe-textfield--floating-label' +
          '.pe-textfield--hide-clear' +
          '.pe-textfield--dirty' +
          (vnode.attrs.colorHasFocus ? '.pe-textfield--focused' : '') +
          '',
        [
          m('.pe-textfield__input-area', [
            m('label.pe-textfield__label', 'Color'),
            m(RgbEditor, {
              value: vnode.attrs.color || 'ffffff',
              onChange: function (state) {
                vnode.attrs.color = state.value
              },
              onFocusChanged: function (hasFocus) {
                vnode.attrs.colorHasFocus = hasFocus
              },
            }),
          ]),
        ],
      ),
    ])
  }

  var editPerson = function (name) {
    var taulaLabel = function (n) {
      var companys = Tomatic.peopleInTable(n)
        .filter(function (item) {
          return item !== name
        })
        .map(function (item) {
          return Tomatic.formatName(item)
        })
        .join(', ')
      if (!companys) {
        companys = 'ningú més'
      }
      return 'Taula ' + n + ': amb ' + companys
    }
    function getDataFromTomatic(name) {
      return {
        newone: name === undefined ? true : false,
        name: name,
        formatName: Tomatic.formatName(name),
        color: Tomatic.persons().colors[name],
        extension: Tomatic.persons().extensions[name],
        email: Tomatic.persons().emails[name],
        erpuser: Tomatic.persons().erpusers[name],
        table: Tomatic.table(name),
      }
    }
    function setDataOnTomatic(name, data) {
      var old = getDataFromTomatic(name)
      var changed = {}
      for (var k in old) {
        if (old[k] !== data[k]) {
          changed[k] = data[k]
        }
      }
      console.log('setDataOnTomatic', name, changed)
      Tomatic.setPersonData(name, data)
    }
    function maxValue(object) {
      var keys = Object.keys(object)
      if (keys.length === 0) return 0
      var values = keys.map(function (key) {
        return object[key]
      })
      return Math.max.apply(null, values)
    }
    function range(n) {
      if (n == 0) return Array()
      return Array.apply(null, Array(n)).map(function (_, i) {
        return i
      })
    }

    var data = getDataFromTomatic(name)
    data.tables = {}
    var tablesToFill = range(maxValue(Tomatic.persons().tables) + 2)
    tablesToFill.map(function (n) {
      data.tables[n] = taulaLabel(n)
    })
    Dialog.show(
      function () {
        return {
          title: 'Edita dades de la persona ' + Tomatic.formatName(name),
          backdrop: true,
          body: [m(PersonEditor, data)],
          footerButtons: [
            m(Button, {
              label: 'Accepta',
              events: {
                onclick: function () {
                  setDataOnTomatic(name, data)
                  Dialog.hide({ id: 'PersonEditor' })
                },
              },
            }),
            m(Button, {
              label: 'Cancel·la',
              events: {
                onclick: function () {
                  Dialog.hide({ id: 'PersonEditor' })
                },
              },
            }),
          ],
          didHide: function () {
            m.redraw()
          },
        }
      },
      { id: 'PersonEditor' },
    )
  }

module.exports =  editPerson

// vim: et sw=2 ts=2
