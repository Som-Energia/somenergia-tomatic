import { Slider } from 'polythene-mithril-slider'
import m from 'mithril'
import {contrast, hex2triplet, triplet2hex} from '../../services/colorutils'

var RgbEditor = {}
RgbEditor.oninit = function (vnode) {
  var state = vnode.state
  state.red = m.prop()
  state.green = m.prop()
  state.blue = m.prop()
  state.setFocus = function (hasFocus) {
    console.log('color has focus', hasFocus)
    vnode.attrs.onFocusChanged && vnode.attrs.onFocusChanged(hasFocus)
  }
  state.setRgb = function () {
    var components = hex2triplet(vnode.attrs.value)
    this.red(components[0])
    this.green(components[1])
    this.blue(components[2])
  }
  state.edited = function () {
    var result = triplet2hex([this.red(), this.green(), this.blue()])
    vnode.attrs.value = result
    vnode.attrs.onChange({ value: result })
  }
  state.setRgb()
}

RgbEditor.view = function (vnode) {
  return m('.rgbeditor.horizontal.layout', [
    m(
      '.field',
      {
        style: {
          'background-color': '#' + vnode.attrs.value,
          color: contrast(vnode.attrs.value),
        },
      },
      vnode.attrs.value,
    ),
    m(
      '.flex.vertical.layout',
      ['red', 'green', 'blue'].map(function (color) {
        return m(Slider, {
          min: 0,
          max: 255,
          class: color,
          value: vnode.state[color](),
          onChange: function (state) {
            vnode.state[color](state.value)
            vnode.state.edited()
          },
          events: {
            onfocus: function (ev) {
              vnode.state.setFocus(true)
            },
            onblur: function (ev) {
              vnode.state.setFocus(false)
            },
          },
        })
      }),
    ),
  ])
}

export default RgbEditor

// vim: et sw=2 ts=2
