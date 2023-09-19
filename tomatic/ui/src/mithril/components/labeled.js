// Wrapps an form input with a label that gets primary color on focus

var m = require('mithril')

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

module.exports = Labeled

// vim: et ts=2 sw=2
