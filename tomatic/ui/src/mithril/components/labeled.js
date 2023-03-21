// Wrapps an form input with a label that gets primary color on focus

module.exports = (function () {
	var m = require('mithril')

	var Labeled = {
		view: function (vnode) {
			labeledId = vnode.children[0].id
			return m('.label-wrapper', [
				m(
					'label.label-wrapper--label',
					{
						for: labeledId,
					},
					vnode.attrs.label
				),
				vnode.children,
				vnode.attrs.help && m('.pe-textfield__help', vnode.attrs.help),
			])
		},
	}

	return Labeled
})()
// vim: noet ts=4 sw=4
