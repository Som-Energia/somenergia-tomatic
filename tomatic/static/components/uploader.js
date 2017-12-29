module.exports = function() {

var m = require('mithril');
var Button = require('polythene-mithril-button');
var jsyaml = require('js-yaml');

var Uploader = {
	controller: function(args) {
		var c = {};
		c.uploadFile = function(ev) {
			var formData = new FormData;
			formData.append(args.name || "file", ev.target.files[0]);
			m.request({
				method: "POST",
				url: args.url,
				data: formData,
				serialize: function(value) {return value},
				deserialize: jsyaml.load,
			}).then(args.onupload, args.onerror);
		};
		return c;
	},
	view: function(c, args) {
		return m('.uploader',
			m('label', [
				m('input[type="file"]', {
					onchange: c.uploadFile.bind(c),
					accept: args.mimetype || "application/x-yaml",
				}),
				m.component(Button, {
					raised: true,
					label: args.label || 'Upload a file...',
				}),
			])
		);
	},
};
return Uploader;
}();


