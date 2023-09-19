// Wrapps an form input with a label that gets primary color on focus

import m from 'mithril'

var Labeled = {
  view: function (vnode) {
    var labeledId = vnode.children[0].id
    return m('.label-wrapper', [
      m(
        'label.label-wrapper--label',
        {
          for: labeledId,
        },
        vnode.attrs.label,
      ),
      vnode.children,
      vnode.attrs.help && m('.pe-textfield__help', vnode.attrs.help),
    ])
  },
}

export default Labeled

// vim: et ts=2 sw=2
