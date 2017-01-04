'use strict';

function hex2triplet(hex) {
	hex = String(hex).replace(/[^0-9a-f]/gi, '');
	if (hex.length < 6) {
		hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
	}
	return [
		hex.substr(0,2),
		hex.substr(2,2),
		hex.substr(4,2)
		].map(function(part) {
			return parseInt(part, 16);
		});
}
function triplet2hex(triplet) {
	var rgb = "#";
	for (let i in triplet) {
		let c = triplet[i];
		let newc = Math.round(Math.min(Math.max(0, c), 255));
		rgb += ("00"+newc.toString(16)).slice(-2);
	}
	return rgb;
}

function luminance(hex, lum) {
	var triplet = hex2triplet(hex);
	lum = lum || 0;
	return triplet2hex(triplet.map(function(c) {
		return c + c*lum;
	}))
}


var Tomatic = {
};

Tomatic.queue = m.prop([]);
Tomatic.init = function() {
	console.log("init",this);
//	this.requestGrid('2016-12-26');
	this.requestQueue();
};
Tomatic.requestQueue = function(suffix) {
	m.request({
		method: 'GET',
		url: 'queue'+(suffix||''),
		deserialize: jsyaml.load,
	}).then(function(response){
		console.log(response);
		if (response.currentQueue!==undefined) {
			Tomatic.queue(response.currentQueue);
		}
	});
};

Tomatic.addLine = function(line) {
	Tomatic.requestQueue('/add/'+line);
};

Tomatic.pauseLine = function(line) {
	Tomatic.requestQueue('/pause/'+line);
};

Tomatic.restoreLine = function(line) {
	Tomatic.requestQueue('/resume/'+line);
};

Tomatic.grid = m.prop({});
Tomatic.requestGrid = function(date) {
	var self = this;
	m.request({
		method: 'GET',
		url: 'graella-'+date+'.yaml',
		deserialize: jsyaml.load,
	}).then(function(data) {
		data.days = data.days || 'dl dm dx dj dv'.split(' ');
		Tomatic.grid(data);
	});
};
Tomatic.formatName = function(name) {
	function titleCase(str)
	{
		return str.replace(/\w\S*/g, function(txt){
			return txt.charAt(0).toUpperCase()
				+ txt.substr(1).toLowerCase();
		});
	}
	if (!name) { return "...";}
	return Tomatic.grid().names[name] || titleCase(name);
};
Tomatic.extension = function(name) {
	return Tomatic.formatName(name) + ": "
		+ (Tomatic.grid().extensions[name] || "???");
};


var QueueWidget = {
	controller: function() {
		var c = {
			addtoqueue: function(ev) {
				console.log("opening dialog");
				console.log('dialog#'+c.dialog.id);
				var dialog = document.querySelector('dialog#'+c.dialog.controller().id);
				if (! dialog.showModal) {
				  dialogPolyfill.registerDialog(dialog);
				}
				dialog.showModal();
			},
			resume: function(line, ev) {
				Tomatic.restoreLine(line);
			},
			pause: function(line, ev) {
				Tomatic.pauseLine(line);
			},
			dialog: m.component(PersonPicker,{
				id: "queueeditorpicker",
				key: "queueeditorpicker",
				title: "Afegir línia oberta",
				onpick: function(name) {
					Tomatic.addLine(name);
				},
				onclose: function() {
				},
			}),
		};
		return c;
	},
	view: function(c) {
		return m('.queueeditor',
			c.dialog,
			Tomatic.queue().map(function(line) {
				return m('.queueitem.'+line.key, {
					'class': line.paused?'paused':'resumed',
					onclick: line.paused?
						c.resume.bind(c,line.key):
						c.pause.bind(c,line.key),
					},
					Tomatic.extension(line.key)
				);
			}),
			m('.queueitem.add', {
				onclick: c.addtoqueue.bind(c),
				},
				"+"
			)
		);
	}
};
var PersonPicker = {
	controller: function(args) {
		var c = {
			id: args.id || 'id'+Math.random(),
			title: args.title || "Escull compa",
			onpick: args.onpick,
			person: m.prop(undefined),

			picked: function(name, ev) {
				console.log("piked", name);
				this.person(name);
				this.close();
				if (this.onpick) {
					this.onpick(name);
				}
			},
			show: function() {
				var dialog = document.querySelector('dialog#'+c.id);
				if (! dialog.showModal) {
					dialogPolyfill.registerDialog(dialog);
				}
				this.person(undefined);
				dialog.showModal()
			},
			close: function() {
				var dialog = document.querySelector('dialog#'+c.id);
				if (! dialog.showModal) {
					dialogPolyfill.registerDialog(dialog);
				}
				dialog.close()
			},
		};
		return c;
	},

	view: function(controller, args) {
		var extensions = Tomatic.grid().extensions || {};
		return (
			m('dialog.mdl-dialog#'+controller.id,
				m('h1.mdl-dialog__title', controller.title),
				m('.mdl-dialog__content',
					m('.extensions',
						Object.keys(extensions).sort().map(function(name) {
							return m('.extension', {
								class: name,
								onclick: controller.picked.bind(controller,name),
								},
								Tomatic.formatName(name)
							);
						})
					)
				),
				m('.mdl-dialog__actions',
					m('button.mdl-button.close[type=button]', {
							onclick: controller.close.bind(controller),
						},
						"Cancel·lar"
					)
				)
			)
		)
	}
};

var WeekList = {
	weeks: m.prop([]),
	current: m.prop(undefined),
	controller: function(parentcontroller) {
		var controller = {
			model: this,
			parent: parentcontroller,
			init: function() {
				self = this;
				m.request({
					method: 'GET',
					url: 'graella/list',
					deserialize: jsyaml.load,
				}).then(function(newWeeklist){
					WeekList.weeks(newWeeklist.weeks.sort().reverse());
					self.setCurrent(newWeeklist.weeks.sort().reverse()[0]);
				});
			},
			setCurrent: function(week)  {
				WeekList.current(week);
				this.parent.loadGrid(week);
			},
		};
		controller.init();
		return controller;
	},
	view: function(c) {
		return m('.weeks',
			this.weeks().map(function(week){
				var current = WeekList.current() === week ? '.current':'';
				return m('.week'+current, {
					onclick: function() {
						c.setCurrent(week);
					}
				}, "Setmana del "+week);
		}));
	}
};


var Graella = Graella || {};

Graella.controller = function(model, args) {
	args = args || {};
	var controller = {
		_editingCell: m.prop(undefined),
		startCellEdition: function(day, houri, turni) {
			this._editingCell({
				day: day,
				houri: houri,
				turni: turni
			});
			var dialog = document.querySelector('dialog#grideditor');
			console.log(dialog);
			if (! dialog.showModal) {
			  dialogPolyfill.registerDialog(dialog);
			}
			dialog.showModal();
		},
		cellEdited: function(name) {
			this.editingCell(name);
			this.editingCell = undefined;
			this._editingCell(undefined);
			var dialog = document.querySelector('dialog#grideditor');
			dialog.close();
		},
		cancelCellEdition: function(ev) {
			this.editingCell = undefined;
			this._editingCell(undefined);
			var dialog = document.querySelector('dialog#grideditor');
			dialog.close();
		},
		dialog: m.component(PersonPicker,{
			id: "grideditor",
			key: "grideditor",
			title: "Editar graella",
			onpick: function(name) {
				console.log(controller._editingCell);
				var day = controller._editingCell().day;
				var houri = controller._editingCell().houri;
				var turni = controller._editingCell().turni;
				Tomatic.grid().timetable[day][houri][turni] = name;
				m.request({
					method: 'UPDATE',
					url: 'graella/'+([
						Tomatic.grid().date,day,houri,turni,name
						].join('/')),
				})
				.then(function() { this.loadGrid(this.d.date);});
			},
			onclose: function() {
				controller.cancelCellEdition();
			},
		}),
		loadGrid: function(date) {
			Tomatic.requestGrid(date)
		},
	};
	controller.loadGrid(args.date ||'2016-12-26');
	return controller;
};

Graella.view = function(c) {
	var cell = function(day, houri, turni) {
		var name = '-';
		try {
			name = Tomatic.grid().timetable[day][houri][turni];
		} catch (err) {
			return m('td','-');
		}
		return m('td', {
				class: name,
				title: Tomatic.extension(name),
				onclick: function(ev) {
					c.startCellEdition(day, houri, turni);
					ev.preventDefault();
				}
			},
			Tomatic.formatName(name)
		);
	};
	var grid = Tomatic.grid();
	return [
		m('style',
			Object.keys(grid.colors||{}).map(function(name) {
				let color = '#'+grid.colors[name];
				return '.'+name+' {\n' +
					'  background-color: '+color+';\n' +
					'  border-color: '+luminance(color,-0.3)+';\n' +
					'  border-width: 2pt;\n'+
				'}\n';
			})
		),
		m('h2', 'Línies actives'),
		m.component(QueueWidget, c),
		m('h2', "Graelles "),
        m('',
            m('',{style: 'display: inline-block; width:100%'},
                m.component(WeekList, c)
            ),
            m('form.uploader', {
                style: 'display: inline-block',
                name: 'upload',
                action: 'graella',
                method: 'post',
                enctype: 'multipart/form-data'
                },
                m('input[type="file"][name="yaml"][accept="application/x-yaml"]'),
                m('input[type="submit"][value="Puja Graella"]')
            )
        ),
		m('h3', 'Setmana ', grid.date),
		c.dialog,
		m('.graella', [
			(grid.days||[]).map(function(day, dayi) {
				return m('.graella', m('table', [
					m('tr', [
						m('td'),
						m('th', {colspan:grid.turns.length}, day),
					]),
					m('td'),
					grid.turns.map(function(turn) {
						return m('th', turn);
					}),
					grid.hours.slice(0,-1).map(function(hour,houri) {
						return m('tr', [
							dayi!=0 && false?
								m('th.separator', m.trust('&nbsp;')) :
								m('th.separator', grid.hours[houri]+'-'+grid.hours[houri+1]),
							grid.turns.map(function(turn, turni) {
								return cell(day, houri, turni)
							}),	
						]);
					}),
				]))
			}),
		]),
		m('h3', 'Extensions'),
		m('.extensions',
			Object.keys(grid.extensions).sort().map(function(name) {
				return m('.extension', {class: name}, [
					Tomatic.formatName(name),
					m('br'),
					grid.extensions[name],
				]);
			})
		),
		m('.extensions',
			Object.keys(grid.otherextensions || {}).sort().map(function(name) {
				return m('.extension', {class: name}, [
					Tomatic.formatName(name),
					m('br'),
					grid.otherextensions[name],
				]);
			})
		),
		m('.graella', [
			m('h5', 'Darrers canvis'),
			m('ul.changelog', [
				grid.log?[]: m('li', 'Cap canvi registrat'),
				(grid.log || []).slice(-5).reverse().map(function(change) {
					return m('li',change);
				}),
				(grid.log || []).length > 5 ?  m('li', m.trust("&hellip;")) : [],
			]),
		]),
		m('.graella', [
			m('h5', 'Penalitzacions'),
			m('ul.penalties', [
				grid.penalties?[]: m('li', 'La graella no te penalitzacions'),
				(grid.penalties || []).slice(-5).reverse().map(function(change) {
					return m('li',change);
				}),
				(grid.penalties || []).length > 5 ?  m('li', m.trust("&hellip;")) : [],
			]),
		]),
	];
};

window.onload = function() {
	Tomatic.init();
	m.mount(document.getElementById("graella"), Graella);
};

