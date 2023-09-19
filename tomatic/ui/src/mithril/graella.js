'use strict'
import m from 'mithril';

import m.prop from 'mithril/stream'

import { Snackbar } from 'polythene-mithril-snackbar';
import { Dialog } from 'polythene-mithril-dialog';
import { Tabs } from 'polythene-mithril-tabs';
import iconMenu from 'mmsvg/google/msvg/navigation/menu';
import iconMore from 'mmsvg/google/msvg/navigation/more-vert';
import Tomatic from '../services/tomatic';
import Login from './components/login';
import PersonsPage from './components/personspage';
import TimeTablePage from './components/timetablepage';
import MenuButton from './components/menubutton';
import LoginPage from './components/loginpage';
import CallInfoPage from './components/callinfopage';
import PbxPage from './components/pbxpage';
import PersonStyles from './components/personstyles';
import extraMenuOptions from '../services/extramenu';
import css from 'polythene-css';
import customStyle from './style.styl';

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
