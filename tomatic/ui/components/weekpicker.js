'use strict';

module.exports = function() {

var m = require('mithril');
var Tomatic = require('./tomatic');

var WeekPicker = {
	oninit: function(vnode) {
		vnode.state.model = this;
		vnode.state.setCurrent = function(week) {
			Tomatic.requestGrid(week);
		};
	},
	view: function(c) {
		return m('.weeks',
			Tomatic.weeks().map(function(week){
				var current = Tomatic.currentWeek() === week ? '.current':'';
				return m('.week'+current, {
					onclick: function() {
						c.state.setCurrent(week);
					}
				}, "Setmana del "+week);
			})
		);
	}
};

return WeekPicker;

}();
// vim: noet sw=4 ts=4
