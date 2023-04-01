module.exports = function() {

var m = require('mithril');
var css = require('@emotion/css').css;
var RaisedButton = require('polythene-mithril-raised-button').RaisedButton;
var api = require('../../services/api');


const uploaderStyle = css`
	label: uploader;
	display: inline-block;
	position: relative;
	overflow: hidden;
	margin: 9px;
	text-align: right;
`
const uploaderInputStyle = css`
	label: uploader-input;
	position: absolute;
	top: 0;
	right: 0;
	margin: 0;
	padding: 0;
	font-size: 20px;
	cursor: pointer;
	opacity: 0;
`

var Uploader = {
	oninit: function(vnode) {
		var c = vnode.state;
		c.uploadFile = function(ev) {
			var formData = new FormData();
			formData.append(vnode.attrs.name || "file", ev.target.files[0]);
			api.request({
				method: "POST",
				url: vnode.attrs.url,
				body: formData,
				serialize: function(value) {return value},
			}).then(vnode.attrs.onupload, vnode.attrs.onerror);
		};
	},
	view: function(vnode) {
		return m('.uploader',
			{className: uploaderStyle },
			m('label', [
				m('input[type="file"]', {
					className: uploaderInputStyle,
					onchange: vnode.state.uploadFile.bind(vnode.state),
					accept: vnode.attrs.mimetype || "application/x-yaml",
				}),
				m(RaisedButton, {
					label: (vnode.attrs.label || 'Upload a file...'),
				}),
			])
		);
	},
};
return Uploader;
}();

// vim: noet ts=4 sw=4
