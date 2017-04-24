module.exports = function() {
	var color = require('./colorutils.js');
	var m = require('mithril');
	var Slider = require('polythene/slider/slider');

	var RgbEditor = {};
	RgbEditor.controller = function(attrs) {
		var ctrl = {};
		ctrl.fetch=attrs.value;
		ctrl.onEdit=attrs.onEdit;
		ctrl.asRgb = function() {
			var result = color.triplet2hex([
				ctrl.red,
				ctrl.green,
				ctrl.blue,
			]);
			return result;
		};
		ctrl.setRgb = function(value) {
			var components = color.hex2triplet(value);
			ctrl.red = components[0];
			ctrl.green = components[1];
			ctrl.blue = components[2];
		};
		ctrl.edited = function() {
			var value = ctrl.asRgb();
			ctrl.onEdit(value);
		};
		return ctrl;
	};

	RgbEditor.view = function(ctrl, attrs) {
		ctrl.fetch=attrs.value;
		ctrl.onEdit=attrs.onEdit;
		ctrl.setRgb(ctrl.fetch());
		return m('.rgbeditor.horizontal.layout', [
			m('.field', {
				style: 'background: #'+ctrl.asRgb(),
			}, ctrl.asRgb()),
			m('.flex.vertical.layout', 
				['red', 'green','blue'].map(function(cls) {
					return m.component(Slider, {
						min: 0,
						max: 255,
						class: cls,
						value: function() {
							return ctrl[cls];
						},
						getValue: function(value) {
							ctrl[cls]=value;
							ctrl.edited();
						},
					});
				})
			)
		]);
	};
	return RgbEditor;
}();

