module.exports = (function () {
  var m = require('mithril')
  var styleCallinfo = require('./callinfo_style.styl')
  var Ripple = require('polythene-mithril-ripple').Ripple
  var Dialog = require('polythene-mithril-dialog').Dialog
  var Button = require('polythene-mithril-button').Button
  var IconButton = require('polythene-mithril-icon-button').IconButton
  var TextField = require('polythene-mithril-textfield').TextField
  var Card = require('polythene-mithril-card').Card
  var ListTile = require('polythene-mithril-list-tile').ListTile
  var List = require('polythene-mithril-list').List
  var Spinner =
    require('polythene-mithril-material-design-spinner').MaterialDesignSpinner
  var CallInfo = require('./callinfo')
  var ContractInfo = require('./contract')
  var PartnerInfo = require('./partnerinfo')
  var Questionnaire = require('./questionnaire')

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

  var typeOfSearch = function () {
    return m(
      'select.select-search#search-by',
      {
        onchange: function () {
          CallInfo.search_by = document.getElementById('search-by').value
        },
      },
      [
        ['phone', 'Telèfon'],
        ['name', 'Cognoms/Nom'],
        ['nif', 'NIF'],
        ['soci', 'Número Soci'],
        ['email', 'Email'],
        ['contract', 'Contracte'],
        ['all', 'Tot'],
      ].map(function (item) {
        const name = item[0]
        const text = item[1]
        return m(
          'option',
          {
            value: name,
            selected: CallInfo.search_by === name,
          },
          text,
        )
      }),
    )
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
        typeOfSearch(),
        m(TextField, {
          className: 'txtf-phone flex',
          placeholder: 'Cerca',
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

  return CallInfoPage
})()
// vim: ts=2 sw=2 et
