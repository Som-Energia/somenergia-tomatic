/// Cal Registry Form

import m from 'mithril'

import { Ripple } from 'polythene-mithril-ripple'
import { Dialog } from 'polythene-mithril-dialog'
import { Button } from 'polythene-mithril-button'
import { ButtonGroup } from 'polythene-mithril-button-group'
import { IconButton } from 'polythene-mithril-icon-button'
import { TextField } from 'polythene-mithril-textfield'
import { ListTile } from 'polythene-mithril-list-tile'
import { List } from 'polythene-mithril-list'
import { RadioGroup } from 'polythene-mithril-radio-group'
import CallInfo from './callinfo'
import Auth from '../../services/auth'

var Questionnaire = {}

var categoryFilter = ''
var isclaim = true

var categoryList = function () {
  var categories = CallInfo.filteredCategories(categoryFilter, isclaim)

  return m(
    '.motius',
    m(List, {
      compact: true,
      indentedBorder: true,
      tiles: categories.map(function (category) {
        var displayText = category.isclaim
          ? '[' +
            (category.section || CallInfo.noSection) +
            '] ' +
            category.name
          : category.name
        return m(ListTile, {
          className:
            CallInfo.call.category === category
              ? 'llista-motius-selected'
              : 'llista-motius-unselected',
          compact: true,
          selectable: true,
          ink: true,
          hover: true,
          title: displayText,
          selected: CallInfo.call.category === category,
          events: {
            onclick: function (ev) {
              CallInfo.call.category = category
            },
          },
          disabled: CallInfo.savingAnnotation,
          bordered: true,
        })
      }),
    }),
  )
}

var clipboardIcon = function () {
  return m('.icon-clipboard', [m('i.far.fa-clipboard')])
}

Questionnaire.annotationButton = function () {
  return m(
    '',
    m(IconButton, {
      icon: clipboardIcon(),
      wash: true,
      compact: true,
      title: 'Anota la trucada fent servir aquest contracte',
      events: {
        onclick: function () {
          Questionnaire.openCaseAnnotationDialog()
        },
      },
      disabled: CallInfo.savingAnnotation || Auth.username() === '',
    }),
  )
}

Questionnaire.openCaseAnnotationDialog = function () {
  var partner = CallInfo.selectedPartner()
  var contract = CallInfo.selectedContract()
  if (CallInfo.call.date === '') {
    CallInfo.call.date = new Date().toISOString()
  }

  var sectionSelector = function () {
    var defaultSection = CallInfo.reasonTag() // From the chosen category
    var sections = CallInfo.selectableSections()
    var selectable = defaultSection === CallInfo.noSection
    return m('', [
      m('p', 'Equip: '),
      m(
        'select',
        {
          id: 'select-user',
          class: '.select-user',
          disabled: !selectable,
          default: defaultSection,
          oninput: function (ev) {
            CallInfo.annotation.tag = ev.target.value
          },
        },
        m(
          'option',
          {
            value: defaultSection,
            selected: !sections.includes(defaultSection),
          },
          defaultSection,
        ),
        selectable &&
          sections.map(function (option) {
            return m(
              'option',
              {
                value: option,
                selected: CallInfo.annotation.tag === option,
              },
              option,
            )
          }),
      ),
    ])
  }

  var resolutionChoser = function () {
    return m('.case-resolution', [
      m('p', 'Resolució:'),
      m(RadioGroup, {
        name: 'resolution',
        onChange: function (state) {
          CallInfo.annotation.resolution = state.value
        },
        checkedValue: CallInfo.annotation.resolution,
        buttons: [
          {
            defaultChecked: true,
            label: 'No resolt',
            value: 'unsolved',
          },
          {
            label: 'Resolt; tenia raó',
            value: 'fair',
          },
          {
            label: 'Resolt; no tenia raó',
            value: 'unfair',
          },
          {
            label: 'Resolt; no es pot gestionar',
            value: 'irresolvable',
          },
        ],
      }),
    ])
  }

  var buttons = function () {
    return [
      m(Button, {
        label: 'Cancel·lar',
        events: {
          onclick: function () {
            Dialog.hide({ id: 'fillReclama' })
          },
        },
        raised: true,
      }),
      m(Button, {
        label: 'Desa',
        events: {
          onclick: function () {
            CallInfo.saveCallLog()
            Dialog.hide({ id: 'fillReclama' })
            Dialog.hide({ id: 'settingsDialog' })
          },
        },
        disabled: CallInfo.hasNoSection(),
        contained: true,
        raised: true,
      }),
    ]
  }

  var emplenaReclamacio = function () {
    CallInfo.resetAnnotation()
    Dialog.show(
      function () {
        return {
          className: 'dialog-reclama',
          title: 'Reclamació:',
          backdrop: true,
          body: [sectionSelector(), m('br'), resolutionChoser()],
          footerButtons: buttons(),
        }
      },
      { id: 'fillReclama' },
    )
  }

  Dialog.show(
    function () {
      var oldAutoRefresh = CallInfo.autoRefresh()
      CallInfo.autoRefresh(false)
      return {
        className: 'card-annotate-case',
        backdrop: true,
        didHide: (id) => {
          CallInfo.autoRefresh(oldAutoRefresh)
        },
        title: 'Anotar trucada',
        body: m('.layout.horizontal', [
          m('.layout.vertical.flex', [
            m('.final-motius', [
              m('strong', 'Trucada:'),
              ' ',
              CallInfo.call.phone || 'Entrada manualment ',
              m('strong', ' el dia '),
              new Date(CallInfo.call.date).toLocaleDateString(),
              m('strong', ' a les '),
              new Date(CallInfo.call.date).toLocaleTimeString(),
            ]),
            m('.final-motius', [
              m('strong', 'De:'),
              ' ',
              partner !== null
                ? [
                    partner.id_soci,
                    partner.dni.replace('ES', ''),
                    partner.name,
                  ].join(' - ')
                : 'Cap persona especificada',
            ]),
            m('.final-motius', [
              m('strong', 'Referent al contracte:'),
              ' ',
              contract !== null
                ? contract.number + ' - ' + contract.cups_adress
                : ' Cap contracte especificat',
            ]),
            m(
              ButtonGroup,
              m(Button, {
                label: 'Reclamació',
                extraWide: true,
                selected: isclaim,
                events: {
                  onclick: function (ev) {
                    if (isclaim) return
                    isclaim = true
                    CallInfo.call.category = ''
                  },
                },
              }),
              m(Button, {
                label: 'Consulta',
                extraWide: true,
                selected: !isclaim,
                events: {
                  onclick: function (ev) {
                    if (!isclaim) return
                    isclaim = false
                    CallInfo.call.category = ''
                  },
                },
              }),
            ),
            m('.reason-filter', [
              m('.motiu', 'Motiu: '),
              m(
                '.filter',
                m(TextField, {
                  className: 'textfield-filter',
                  label: 'Escriu per a filtrar',
                  value: categoryFilter,
                  dense: true,
                  onChange: function (ev) {
                    categoryFilter = ev.value
                  },
                }),
              ),
            ]),
            categoryList(),
            m('.final-motius', [
              m(TextField, {
                className: 'textfield-comentaris',
                label: 'Comentaris',
                help: 'Especifica més informació',
                multiLine: true,
                floatingLabel: true,
                rows: 5,
                dense: true,
                value: CallInfo.call.notes,
                onChange: function (params) {
                  CallInfo.call.notes = params.value
                },
                disabled: CallInfo.savingAnnotation,
              }),
            ]),
          ]),
        ]),
        footerButtons: [
          m(Button, {
            label: 'Sortir',
            events: {
              onclick: function () {
                Dialog.hide({ id: 'settingsDialog' })
              },
            },
            raised: true,
          }),
          m(
            Button,
            {
              className: 'save',
              label: CallInfo.savingAnnotation
                ? 'Desant'
                : isclaim
                ? 'Continua'
                : 'Desa',
              events: {
                onclick: function () {
                  if (isclaim) {
                    emplenaReclamacio()
                  } else {
                    CallInfo.saveCallLog()
                    Dialog.hide({ id: 'settingsDialog' })
                  }
                },
              },
              border: 'true',
              disabled:
                CallInfo.savingAnnotation ||
                CallInfo.call.category === '' ||
                CallInfo.call.notes === '' ||
                Auth.username() === '',
            },
            m(Ripple),
          ),
        ],
      }
    },
    { id: 'settingsDialog' },
  )
}

export default Questionnaire

// vim: ts=2 sw=2 et
