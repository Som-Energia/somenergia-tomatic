module.exports = function() {

var m = require('mithril');
var RaisedButton = require('polythene-mithril-raised-button').RaisedButton;
var jsyaml = require('js-yaml');

var Uploader = {
	oninit: function(vnode) {
		var c = vnode.state;
		c.uploadFile = function(ev) {
			var formData = new FormData;
			formData.append(vnode.attrs.name || "file", ev.target.files[0]);
			m.request({
				method: "POST",
				url: vnode.attrs.url,
				data: formData,
				serialize: function(value) {return value},
				deserialize: jsyaml.load,
			}).then(vnode.attrs.onupload, vnode.attrs.onerror);
		};
	},
	view: function(vnode) {
		return m('.uploader',
			m('label', [
				m('input[type="file"]', {
					onchange: vnode.state.uploadFile.bind(vnode.state),
					accept: vnode.attrs.mimetype || "application/x-yaml",
				}),
				m(RaisedButton, {
					raised: true,
					label: vnode.attrs.label || 'Upload a file...',
				}),
			])
		);
	},
};
return Uploader;
}();


