'use strict'
var m = require('mithril')

m.prop = require('mithril/stream')

var Snackbar = require('polythene-mithril-snackbar').Snackbar
var Dialog = require('polythene-mithril-dialog').Dialog
var Tabs = require('polythene-mithril-tabs').Tabs

var iconMenu = require('mmsvg/google/msvg/navigation/menu')
var iconMore = require('mmsvg/google/msvg/navigation/more-vert')

var Tomatic = require('../services/tomatic')
var Login = require('./components/login')
var PersonsPage = require('./components/personspage').default
var TimeTablePage = require('./components/timetablepage')
var MenuButton = require('./components/menubutton')
var LoginPage = require('./components/loginpage')
var CallInfoPage = require('./components/callinfopage')
var PbxPage = require('./components/pbxpage').default
var PersonStyles = require('./components/personstyles').default
var Doc = require('./components/doc').default
var extraMenuOptions = require('../services/extramenu').default

var css = require('polythene-css')
var customStyle = require('./style.styl')

css.addLayoutStyles()
css.addTypography()

const SnackbarLogger = function () {
  return {
    log: function (message) {
      Snackbar.show({
        containerSelector: '#snackbar',
        title: message,
      })
    },
    error: function (message) {
      Snackbar.show({
        containerSelector: '#snackbar',
        title: message,
        className: 'error',
        timeout: 10,
      })
    },
  }
}
Tomatic.loggers.push(SnackbarLogger())

const toolbarRow = function (title) {
  return m('.pe-dark-tone.pe-toolbar.flex.layout', [
    m(MenuButton, {
      icon: iconMenu,
      origin: 'top-left',
    }),
    m('.flex', title),
    Login.identification(),
    m(MenuButton, {
      id: 'right-menu',
      icon: iconMore,
      origin: 'top-right',
      options: extraMenuOptions(),
    }),
  ])
}

const applicationPages = ['Graelles', 'Centraleta', 'Persones', 'Trucada']

var tabs = applicationPages.map(function (name) {
  return {
    label: name,
    element: m.route.Link,
    url: {
      href: '/' + name,
    },
  }
})
const indexForRoute = function (route) {
  return tabs.reduce(function (previousValue, tab, index) {
    if (route === tab.url.href) {
      return index
    } else {
      return previousValue
    }
  }, 0)
}

var TomaticApp = {}
TomaticApp.view = function (vnode) {
  //console.log("Page: ", m.route.get());
  var currentTabIndex = indexForRoute(m.route.get())
  return m(
    '' +
      (Tomatic.isKumatoMode() ? '.pe-dark-tone' : '') +
      ('.variant-' + Tomatic.variant),

    [
      PersonStyles(),
      m('', [
        m('.tmt-header', [
          m('.tmt-header__dimmer'),
          toolbarRow('Tomàtic - Som Energia'),
          m(Tabs, {
            tabs: tabs,
            activeSelected: true,
            selectedTab: currentTabIndex,
          }),
        ]),
        vnode.children,
        m('#snackbar', m(Snackbar)),
        m(Dialog),
      ]),
    ],
  )
}

window.onload = function () {
  Tomatic.init()
  //m.redraw.strategy('diff');
  var element = document.getElementById('tomatic')
  m.route(element, '/Graelles', {
    '/Graelles': {
      render: () => m(TomaticApp, m(TimeTablePage)),
    },
    '/Centraleta': {
      render: () => m(TomaticApp, m(PbxPage)),
    },
    '/Persones': {
      render: () => m(TomaticApp, m(PersonsPage)),
    },
    '/Trucada': {
      render: () => m(TomaticApp, m(CallInfoPage)),
    },
    '/Login': {
      render: () => m(TomaticApp, m(LoginPage)),
    },
  })
}
// vim: noet ts=4 sw=4
