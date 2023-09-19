// MenuButton
import m from 'mithril'

import { IconButton } from 'polythene-mithril-icon-button'
import { ListTile } from 'polythene-mithril-list-tile'
import { List } from 'polythene-mithril-list'
import { Shadow } from 'polythene-mithril-shadow'
import { Menu } from 'polythene-mithril-menu'
import iconMore from 'mmsvg/google/msvg/navigation/more-vert'

const MenuContent = function (options) {
  return m(List, {
    compact: true,
    tiles: options.map(function (item) {
      return m(ListTile, {
        title: item.title,
        ink: true,
        hoverable: true,
        className: 'colored',
        disabled: item.disabled,
        front: item.icon,
        events: {
          onclick: item.action,
        },
      })
    }),
  })
}

// id: id for the button or `the_menu` by default
// icon: svg icon
// origin: 'top-left', 'bottom-up', 'top-right'
// options: list[{title, action}]

const MenuButton = {
  oninit: function (vnode) {
    vnode.state.shown = false
    vnode.attrs.id = vnode.attrs.id || 'the_menu'
  },
  view: function (vnode) {
    var attrs = vnode.attrs
    return m(
      '',
      {
        style: {
          position: 'relative',
        },
      },
      [
        m(Shadow),
        m(Menu, {
          target: '#' + attrs.id,
          origin: attrs.origin || false,
          size: 5,
          offset: 30,
          show: vnode.state.shown,
          didHide: function () {
            vnode.state.shown = false
          },
          content: MenuContent(attrs.options || []),
        }),
        m(IconButton, {
          icon: {
            svg: attrs.icon || iconMore,
          },
          className: 'colored',
          id: attrs.id,
          events: {
            onclick: function (ev) {
              vnode.state.shown = true
            },
          },
        }),
      ],
    )
  },
}

export default MenuButton
// vim: et sw=2 ts=2
