import m from 'mithril'
import styleCallinfo from './callinfo_style.styl'
import { Ripple } from 'polythene-mithril-ripple'
import { Dialog } from 'polythene-mithril-dialog'
import { Button } from 'polythene-mithril-button'
import { IconButton } from 'polythene-mithril-icon-button'
import { TextField } from 'polythene-mithril-textfield'
import { Card } from 'polythene-mithril-card'
import { ListTile } from 'polythene-mithril-list-tile'
import { List } from 'polythene-mithril-list'
import { MaterialDesignSpinner as Spinner } from 'polythene-mithril-material-design-spinner'
import CallInfo from './callinfo'
import ContractInfo from './contract'
import PartnerInfo from './partnerinfo'
import Questionnaire from './questionnaire'
import Select from './select'
import autofiltertype from '../../services/autofiltertype'

var CallInfoPage = {}

var searchIcon = function () {
  return m('.icon-search', [m('i.fas.fa-search')])
}

var lockIcon = function () {
  return m('.icon-lock', [m('i.fas.fa-lock-open')])
}

var lockedIcon = function () {
  return m('.icon-lock', [m('i.fas.fa-lock')])
}

var newTabIcon = function () {
  return m('.icon-new-tab', [m('i.fas.fa-external-link-alt')])
}

var refreshIcon = function () {
  return m('.icon-refresh', [m('i.fas.fa-redo-alt')])
}

var typeOfSearch = function (fieldguess) {
  const fields = {
    phone: 'Telèfon',
    name: 'Cognoms/Nom',
    nif: 'NIF',
    soci: 'Número Soci',
    email: 'Email',
    contract: 'Contracte',
    cups: 'CUPS',
    all: 'Tot',
  }

  const options = Object.assign(
    { '': 'Auto' + (fieldguess ? ` (${fields[fieldguess]})` : '') },
    fields,
  )

  return m(Select, {
    className: 'select-search flex',
    label: 'Criteri',
    required: true,
    onChange: function (ev) {
      CallInfo.search_by = ev.target.value
    },
    value: CallInfo.search_by,
    options: options,
  })
}

CallInfoPage.settingsDialog = function () {
  Dialog.show(
    function () {
      return {
        className: 'dialog-settings',
        title: 'Configuració:',
        backdrop: true,
        body: [
          m(
            Button,
            {
              className: 'btn-refresh',
              label: refreshIcon(),
              border: 'true',
              disabled: CallInfo.updatingCategories,
              events: {
                onclick: function () {
                  CallInfo.updateCategories()
                },
              },
            },
            m(Ripple),
          ),
          CallInfo.updatingCategories
            ? [
                m('b', 'Actualitzar categories (Trucades Telefòniques)'),
                m('div', 'Pot portar el seu temps, pots sortir mentrestant.'),
              ]
            : m('b', 'Actualitzar categories (Trucades Telefòniques)'),
        ],
        footerButtons: m(Button, {
          label: 'Sortir',
          events: {
            onclick: function () {
              Dialog.hide({ id: 'settingsDialog' })
            },
          },
          raised: true,
        }),
      }
    },
    { id: 'settingsDialog' },
  )
}

var customerSearch = function () {
  function keyEventHandler(event) {
    var char = event.which || event.keyCode
    if (char === 13) {
      CallInfo.searchCustomer()
    }
  }
  return m('', { className: 'busca-info' }, [
    m('.busca-info-title.layout.horizontal', [
      typeOfSearch(autofiltertype(CallInfo.search.trim())),
      m(TextField, {
        className: 'search-query flex',
        placeholder: 'Cerca',
        floatingLabel: true,
        value: CallInfo.search,
        onChange: function (state) {
          CallInfo.search = state.value
        },
        events: {
          onkeypress: function (event) {
            keyEventHandler(event)
          },
        },
        disabled: !CallInfo.autoRefresh,
      }),
      m(IconButton, {
        className: 'btn-search',
        icon: searchIcon(),
        compact: true,
        events: {
          onclick: function () {
            CallInfo.searchCustomer()
          },
        },
        disabled: !CallInfo.autoRefresh,
      }),
    ]),
  ])
}

var responsesMessage = function (info) {
  var time = new Date(info.date).toLocaleTimeString()
  return m(
    '',
    m('span.time', time),
    ' ',
    m('span.phone', info.phone ? info.phone : 'Registre Manual'),
    m.trust('&nbsp;'),
    m.trust('&nbsp;'),
    info.reason
      ? m(
          'span.partner',
          { title: 'Persona Atesa' },
          info.partner ? info.partner : 'Sense informació',
        )
      : '',
    info.reason && info.contract
      ? [
          m.trust('&nbsp;'),
          m('span.contract', { title: 'Contracte' }, info.contract),
        ]
      : '',
    !info.reason ? m('span.pending', " Pendent d'anotar") : '',
    '',
  )
}

var attendedCallList = function () {
  var aux = []
  if (CallInfo.callLog.length === 0) {
    return m(
      '.attended-calls-list',
      m(List, {
        compact: true,
        tiles: [
          m(ListTile, {
            className: 'registres',
            compact: true,
            title: 'Cap trucada al registre.',
          }),
        ],
      }),
    )
  }
  var currentDate = new Date().toLocaleDateString()
  var items = CallInfo.callLog
    .slice(0)
    .reverse()
    .map(function (item, index) {
      var isSelected = CallInfo.isLogSelected(item.date)
      var itemClicked = function (ev) {
        if (item.reason !== '') return
        CallInfo.toggleLog(item.date, item.phone)
      }
      var needsDate = false
      var itemDate = new Date(item.date).toLocaleDateString()
      var itemWeekDay = new Date(item.date).toLocaleDateString(undefined, {
        weekday: 'long',
      })
      if (itemDate !== currentDate) {
        currentDate = itemDate
        needsDate = true
      }
      var missatge = responsesMessage(item)
      var solved = item.reason !== ''
      return [
        needsDate
          ? m(ListTile, {
              className: 'registres dateseparator',
              title: itemWeekDay + ' ' + itemDate,
              header: true,
              disabled: true,
            })
          : '',
        m(ListTile, {
          className: 'registres' + (isSelected ? ' selected' : ''),
          selectable: true,
          hoverable: !solved,
          ink: !solved,
          title: missatge,
          subtitle: item.reason,
          selected: false,
          events: {
            onclick: itemClicked,
          },
          disabled: !CallInfo.autoRefresh,
        }),
      ]
    })
  return m('.attended-calls-list', m(List, { compact: true, tiles: items }))
}

var attendedCalls = function () {
  return m(Card, {
    className: 'card-attended-calls',
    content: [
      {
        primary: {
          title: m('.layout.horizontal', [
            m('.title', 'Trucades ateses'),
            m('.flex'), // expanding spacer
            m(IconButton, {
              className: 'btn-lock',
              icon: CallInfo.autoRefresh ? lockIcon() : lockedIcon(),
              border: false,
              wash: true,
              compact: true,
              title: CallInfo.autoRefresh
                ? 'Actualitza el cas automàticament'
                : 'Fixa el cas actual',
              events: {
                onclick: function () {
                  CallInfo.autoRefresh = !CallInfo.autoRefresh
                },
              },
            }),
            m(IconButton, {
              className: 'btn-new-tab',
              icon: newTabIcon(),
              border: false,
              wash: true,
              compact: true,
              title: 'Obre una nova pestanya',
              url: {
                href: window.location,
                target: '_blank',
              },
            }),
            Questionnaire.annotationButton(),
          ]),
        },
      },
      {
        text: {
          content:
            CallInfo.callLog[0] === 'lookingfor'
              ? m('center', m(Spinner, { show: 'true' }))
              : attendedCallList(),
        },
      },
    ],
  })
}

CallInfoPage.view = function () {
  return m('.callinfo', [
    m('.all-info-call.layout.horizontal', [
      attendedCalls(),
      m('.layout.horizontal.flex', [
        m('.layout.vertical.flex', [
          customerSearch(),
          m(
            '.plane-info',
            CallInfo.searchStatus() === 'ZERORESULTS'
              ? m('.searching', "No s'ha trobat cap resultat.")
              : CallInfo.searchStatus() === 'SEARCHING'
              ? m('.searching', m(Spinner, { show: 'true' }))
              : CallInfo.searchStatus() === 'ERROR'
              ? m('.searching', "S'ha produït un error en la cerca.")
              : CallInfo.searchStatus() === 'TOOMANYRESULTS'
              ? m(
                  '.searching',
                  'Cerca poc específica, retorna masses resultats.',
                )
              : m('.plane-info', [
                  m('.layout.vertical.flex', [
                    PartnerInfo.allInfo(CallInfo.searchResults),
                    ContractInfo.mainPanel(CallInfo.searchResults),
                  ]),
                  ContractInfo.detailsPanel(CallInfo.searchResults),
                ]),
          ),
        ]),
      ]),
    ]),
  ])
}

export default CallInfoPage

// vim: ts=2 sw=2 et
