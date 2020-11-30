module.exports = function() {
	var color = require('./colorutils.js');
	var m = require('mithril');

	var Slider = require('polythene-mithril-slider').Slider;

	var RgbEditor = {};
	RgbEditor.oninit = function(vnode) {
		var state = vnode.state;
		state.red = m.prop();
		state.green = m.prop();
		state.blue = m.prop();
		state.setRgb = function() {
			var components = color.hex2triplet(vnode.attrs.value);
			this.red(components[0]);
			this.green(components[1]);
			this.blue(components[2]);
		};
		state.edited = function() {
			var result = color.triplet2hex([
				this.red(),
				this.green(),
				this.blue(),
			]);
			vnode.attrs.value=result;
			vnode.attrs.onChange({value: result});
		};
		state.setRgb();
	};

	RgbEditor.view = function(vnode) {
		return m('.rgbeditor.horizontal.layout', [
			m('.field', {
				style: {
					'background-color': '#'+vnode.attrs.value,
					color: color.contrast(vnode.attrs.value),
				},
			}, vnode.attrs.value),
			m('.flex.vertical.layout', 
				['red', 'green','blue'].map(function(color) {
					return m(Slider, {
						min: 0,
						max: 255,
						className: color,
						value: vnode.state[color],
						onChange: function(state) {
							vnode.state[color](state.value);
							vnode.state.edited();
						},
					});
				})
			),
		]);
	};
	return RgbEditor;
}();

