'use strict';

// Queue Monitor
// Monitors and controls the PBX queue status

module.exports = function() {

var m = require('mithril');
var Tomatic = require('./tomatic')
var PersonPicker = require('./personpicker')

var QueueMonitor = {
	oninit: function(vnode) {
		vnode.state.addtoqueue = function(ev) {
			Dialog.show({
				id: 'QueuePersonPicker',
				title: 'Obre una nova línia amb:',
				backdrop: true,
				body: [
					m(PersonPicker, {
						id:'QueuePersonPicker',
						onpick: function(name) {
							Dialog.hide({id: 'QueuePersonPicker'});
							Tomatic.addLine(name);
						}
					}),
				],
				footerButtons: [
					m(Button, {
						label: "Tanca",
						events: {
							onclick: function() {
								Dialog.hide({id: 'QueuePersonPicker'});
							},
						},
					}),
				],
			}, {id: 'QueuePersonPicker'});
		};
		vnode.state.resume = function(line, ev) {
			Tomatic.restoreLine(line);
		};
		vnode.state.pause = function(line, ev) {
			Tomatic.pauseLine(line);
		};
	},
	view: function(vnode) {
		return m('.queueeditor',
			Tomatic.queue().map(function(line) {
				return m('.queueitem.'
					+ line.key
					+ (line.paused?'.paused':'.resumed')
					+ (line.disconnected?".disconnected":"")
					+ (line.ringing?".ringing":"")
					+ (line.incall?".incall":"")
					, {
					onclick: line.paused?
						vnode.state.resume.bind(vnode.state,line.key):
						vnode.state.pause.bind(vnode.state,line.key),
					key: line.key,
					title: (''
						+ (line.paused?"Pausa. ":'')
						+ (line.disconnected?"Desconexió. ":"")
						+ (line.ringing?"Ring!! ":"")
						+ (line.incall?"En Trucada. ":"")
					) || "Disponible.",
					},
					Tomatic.extension(line.key)
				);
			}),
			m('.queueitem.add', {
				onclick: vnode.state.addtoqueue.bind(vnode.state),
				},
				"+"
			)
		);
	}
};

return QueueMonitor;

}()
// vim: noet ts=4 sw=4
