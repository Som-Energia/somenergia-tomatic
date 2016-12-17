'use strict';

var PersonPicker = {
	controller: function(persons) {
		return {
			personPicked: function(person) {
				persons.cellEdited(person);
			},
		};
	},

	view: function(controller, persons) {
		return (
			m('dialog.mdl-dialog[open]',
				m('h1.mdl-dialog__title', "Qui farà el torn?"),
				m('.mdl-dialog__content',
					m('.extensions',

						Object.keys(persons.d.extensions).sort().map(function(name) {
							return m('.extension', {
								class: name,
								onclick: function(ev) {
									controller.personPicked(name);
								}},
								persons.formatName(name)
							);
						})
					)
				),
				m('.mdl-dialog__actions',
					m('button.mdl-button.close[type=button]', {
							onclick: persons.cancelCellEdition,
						},
						"Cancel·lar"
					)
				)
			)
		)
	}
};


var Graella = Graella || {};

Graella.controller = function(model, args) {
	args = args || {};
	var controller = {
		_editingCell: m.prop(undefined),
		formatName: function(name) {
			function titleCase(str)
			{
				return str.replace(/\w\S*/g, function(txt){
					return txt.charAt(0).toUpperCase()
						+ txt.substr(1).toLowerCase();
				});
			}
			if (!name) { return "...";}
			return this.d.names[name] || titleCase(name);
		},
		extension: function(name) {
			return this.formatName(name) + ": "
				+ (this.d.extensions[name] || "???");
		},
		editCell: function(day, houri, turni) {
			this._editingCell({
				day: day,
				houri: houri,
				turni: turni
			});
			var dialog = document.querySelector('dialog');
			this.cellSelected = function(newName) {
				this.d.timetable[day][houri][turni] = newName;
				m.request({
					method: 'UPDATE',
					url: 'editgraella/'+([
						this.d.date,day,houri,turni,newName
						].join('/')),
				})
				.then(function() { this.loadGrid(this.d.date);});
			}
			if (! dialog.showModal) {
			  dialogPolyfill.registerDialog(dialog);
			}
			dialog.showModal();
		},
		cellEdited: function(name) {
			var dialog = document.querySelector('dialog');
			this.cellSelected(name);
			this.cellSelected = undefined;
			this._editingCell(undefined);
			dialog.close();
		},
		cancelCellEdition: function(ev) {
			var dialog = document.querySelector('dialog');
			this.cellSelected = undefined;
			this._editingCell(undefined);
			dialog.close();
		},
		loadGrid: function(date) {
			var self = this;
			m.request({
				method: 'GET',
				url: 'graella-'+date+'.yaml',
				deserialize: jsyaml.load,
			}).then(function(newGrid){
				console.log("Nova grid",newGrid);
				self.d = newGrid;
			});
		},
	};
	controller.loadGrid(args.date ||'2016-02-02');
	return controller;
};

Graella.view = function(c) {
	var cell = function(day, houri, turni) {
		var name = '-';
		try {
			name = c.d.timetable[day][houri][turni];
		} catch (err) {
			return m('td','-');
		}
		return m('td', {
				class: name,
				title: c.extension(name),
				onclick: function(ev) {
					c.editCell(day, houri, turni);
					ev.preventDefault();
				}
			},
			c.formatName(name)
		);
	};
	return [
		c._editingCell() ? m.component(PersonPicker, c):[], 
		m('h1', "Setmana ", c.d.date),
		m('table', [
			m('tr', c.d.days.map(function(day) {
				return [
					m('td'),
					m('th', {colspan:c.d.turns.length}, day),
				];
			})),
			m('tr', c.d.days.map(function(day) {
				return [
					m('td'),
					c.d.turns.map(function(turn) {
						return m('th', turn);
					}),
				];
			})),
			c.d.hours.slice(0,-1).map(function(hour,houri) {
				return m('tr', [
					c.d.days.map(function(day, dayi) {
						return [
							dayi!=0?
								m('td', m.trust('&nbsp;')) :
								m('th', c.d.hours[houri]+'-'+c.d.hours[houri+1]),
							c.d.turns.map(function(turn, turni) {
								return cell(day, houri, turni)
							}),	
						];
					}),
				]);
			}),
		]),
		m('h3', 'Extensions'),
		m('.extensions',
			Object.keys(c.d.extensions).sort().map(function(name) {
				return m('.extension', {class: name}, [
					c.formatName(name),
					m('br'),
					c.d.extensions[name],
				]);
			})
		),
		m('.extensions',
			Object.keys(c.d.otherextensions).sort().map(function(name) {
				return m('.extension', {class: name}, [
					c.formatName(name),
					m('br'),
					c.d.otherextensions[name],
				]);
			})
		),
	];
};

window.onload = function() {
	m.mount(document.getElementById("graella"), Graella);
};

