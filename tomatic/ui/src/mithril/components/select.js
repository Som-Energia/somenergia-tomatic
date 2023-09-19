'use strict'
module.exports = (function () {
  var m = require('mithril')

  m.prop = require('mithril/stream')

  var Select = {
    oninit: function (vnode) {
      vnode.state.value = m.prop(vnode.attrs.value)
      vnode.state.hasFocus = false
      vnode.state.setFocus = function setFocus(hasFocus) {
        console.log('Getting focus:', hasFocus)
        vnode.state.hasFocus = hasFocus
      }
    },
    view: function (vnode) {
      const { label, required, onChange, options, ...remaining} = vnode.attrs
      return m(
        '.pe-textfield.pe-textfield--floating-label' +
          '.pe-textfield--hide-clear.pe-textfield--dirty' +
          (vnode.state.hasFocus ? '.pe-textfield--focused' : '') +
          (required !== undefined ? '.pe-textfield--required' : ''),
		  remaining,
        [
          m('.pe-textfield__input-area', [
            m('label.pe-textfield__label', label),
            m(
              'select.pe-textfield__input',
              {
                value: vnode.state.value(),
                onchange: function (ev) {
                  vnode.state.value(ev.target.value)
                  onChange(ev)
                },
                onfocus: function (ev) {
                  vnode.state.setFocus(true)
                },
                onblur: function (ev) {
                  vnode.state.setFocus(false)
                },
              },
              Object.keys(options).map(function (value) {
                return m(
                  'option',
                  {
                    value: value,
                  },
                  options[value],
                )
              }),
            ),
          ]),
        ],
      )
    },
  }

  return Select
})()

// vim: noet ts=4 sw=4
