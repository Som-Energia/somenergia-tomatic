// PersonPicker
// Displays a list of persons as colored boxes
// to choose one by clicking on them.
// Attributes:
// - onpick: callback to be called on pick
// - nobodyPickable: bool 'nobody' is an option or not

import m from 'mithril'

import Tomatic from '../../services/tomatic'

var PersonPicker = {
  oninit: function (vnode) {
    vnode.state.onpick = vnode.attrs.onpick
    vnode.state.person = m.prop(undefined)
    vnode.state.picked = function (name, ev) {
      vnode.state.person(name)
      if (vnode.attrs.onpick) {
        vnode.attrs.onpick(name)
      }
    }
  },
  view: function (vnode) {
    var pickCell = function (name) {
      return m(
        '.extension',
        {
          className: name,
          onclick: vnode.state.picked.bind(vnode, name),
        },
        Tomatic.formatName(name),
      )
    }
    var extensions = Tomatic.persons().extensions || {}
    return m('.extensions', [
      Object.keys(extensions).sort().map(pickCell),
      vnode.attrs.nobodyPickable ? pickCell('ningu') : [],
    ])
  },
}

export default PersonPicker

// vim: et sw=2 ts=2
