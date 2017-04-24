'use strict';
var m = require('mithril');
var jsyaml = require('js-yaml');
var Layout = require('polythene/layout/theme/theme');
var SnackBar = require('polythene/notification/snackbar');
var Button = require('polythene/button/button');
var Dialog = require('polythene/dialog/dialog');
var Ripple = require('polythene/ripple/ripple');
var Card = require('polythene/card/card');
var HeaderPanel = require('polythene/header-panel/header-panel');
var IconButton = require('polythene/icon-button/icon-button');
var Icon = require('polythene/icon/icon');
var Tabs = require('polythene/tabs/tabs');
var Textfield = require('polythene/textfield/textfield');
var iconMenu = require('mmsvg/google/msvg/navigation/menu');
var iconMore = require('mmsvg/google/msvg/navigation/more-vert');
var RgbEditor = require('./components/rgbeditor');

var theme = require('polythene/theme/theme');
var customStyle = require('./style.styl');
var luminance = require('./components/colorutils').luminance;

const applicationPages = [
	"Graelles",
	"Centraleta",
	"Persones",
	"Trucada",
	].map(function(n) {return {label:n};});


var Tomatic = {
};

Tomatic.queue = m.prop([]);
Tomatic.editedPerson=m.prop('erola');
Tomatic.init = function() {
	this.requestWeeks();
	this.requestQueue();
};
Tomatic.requestQueue = function(suffix) {
	m.request({
		method: 'GET',
		url: '/api/queue'+(suffix||''),
		deserialize: jsyaml.load,
	}).then(function(response){
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

Tomatic.requestGrid = function(week) {
	m.request({
		method: 'GET',
		url: '/api/graella-'+week+'.yaml',
		deserialize: jsyaml.load,
	}).then(function(data) {
		data.days = data.days || 'dl dm dx dj dv'.split(' ');
		Tomatic.currentWeek(week);
		Tomatic.grid(data);
	});
};
Tomatic.weekday = function(short) {
	return {
		dl: 'Dilluns',
		dm: 'Dimarts',
		dx: 'Dimecres',
		dj: 'Dijous',
		dv: 'Divendres',
	}[short] || '??';
};
Tomatic.formatName = function(name) {
	function titleCase(str)
	{
		return str.replace(/\w\S*/g, function(txt){
			return txt.charAt(0).toUpperCase()
				+ txt.substr(1).toLowerCase();
		});
	}
	if (!name) { return "-";}
	return (Tomatic.grid().names||{})[name] || titleCase(name);
};
Tomatic.peopleInTable = function(table) {
	var tables = Tomatic.grid().tables;
	var result = Object.keys(tables).filter(function(k) {
		return Tomatic.grid().tables[k]===table;
		});
	return result;
};
Tomatic.extension = function(name) {
	return Tomatic.formatName(name) + ": "
		+ ((Tomatic.grid().extensions||{})[name] || "???");
};
Tomatic.cell = function(day, houri, turni) {
	try {
		return Tomatic.grid().timetable[day][houri][turni];
	} catch(err) {
		return undefined;
	}
};
Tomatic.editCell = function(day,houri,turni,name) {
	// Direct edition, just for debug purposes
	//Tomatic.grid().timetable[day][houri][turni] = name;
	m.request({
		method: 'UPDATE',
		url: '/api/graella/'+([
			Tomatic.grid().week,day,houri,turni,name
			].join('/')),
		deserialize: jsyaml.load,
	})
	.then( function(data) {
		Tomatic.requestGrid(Tomatic.grid().week);
	}, function(error) {
		Tomatic.error("Problemes editant la graella: "+
			(error.error || "Inexperat"));
	});
};


Tomatic.weeks = m.prop([]);
Tomatic.currentWeek = m.prop(undefined);
Tomatic.requestWeeks = function() {
	m.request({
		method: 'GET',
		url: '/api/graella/list',
		deserialize: jsyaml.load,
	}).then(function(newWeeklist){
		let weeks = newWeeklist.weeks.sort().reverse();
		Tomatic.weeks(weeks);
		if (Tomatic.currentWeek()===undefined) {
			let expirationms = 1000*60*60*(24*4 + 18);
			let oldestWeek = new Date(new Date().getTime()-expirationms);
			let current = undefined;
			for (let i in weeks) {
				if (current!==undefined && new Date(weeks[i])<oldestWeek) {
					break;
				}
				current = weeks[i];
			}
			if (current!==undefined) {
				Tomatic.requestGrid(current);
			}
		}
	});
};

Tomatic.log = function(message) {
	console.log("log: ", message);
	SnackBar.show({
		containerSelector: '#snackbar',
		title: message,
	});
};

Tomatic.error = function(message) {
	console.log("error: ", message, ...arguments);
	SnackBar.show({
		containerSelector: '#snackbar',
		title: message,
		class: 'error',
	});
};

var Uploader = {
	controller: function(args) {
		var c = {};
		c.uploadFile = function(ev) {
			var formData = new FormData;
			formData.append("yaml", ev.target.files[0]);
			m.request({
				method: "POST",
				url: args.url,
				data: formData,
				serialize: function(value) {return value},
				deserialize: jsyaml.load,
			}).then(function(result) {
				Tomatic.init();
			}, function(error) {
				console.log("Upload error:", error);
				Tomatic.error("Upload error: " + error.error);
			});
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

var Todo = function(message) {
	return m.component(Card, {
		content: [{
			primary: {
				title: 'TODO',
				subtitle: message,
			},
		}],
	});
};


var QueueWidget = {
	controller: function() {
		var c = {
			addtoqueue: function(ev) {
				Dialog.show({
					title: 'Obre una nova línia amb:',
					body: [
						m.component(PersonPicker, {
							id:'QueuePersonPicker',
							onpick: function(name) {
								Dialog.hide('QueuePersonPicker');
								Tomatic.addLine(name);
							}
						}),
					],
					footer: [
						m.component(Button, {
							label: "Cancel·la",
							events: {
								onclick: function() {
									Dialog.hide('QueuePersonPicker');
								},
							},
						}),
					],
				}, 'QueuePersonPicker');
			},
			resume: function(line, ev) {
				Tomatic.restoreLine(line);
			},
			pause: function(line, ev) {
				Tomatic.pauseLine(line);
			},
		};
		return c;
	},
	view: function(c) {
		return m('.queueeditor',
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
			onpick: args.onpick,
			nobodyPickable: args.nobodyPickable,
			person: m.prop(undefined),
			picked: function(name, ev) {
				this.person(name);
				if (this.onpick) {
					this.onpick(name);
				}
			},
		};
		return c;
	},

	view: function(controller, args) {
		var pickCell = function(name) {
			return m('.extension', {
				class: name,
				onclick: controller.picked.bind(controller,name),
				},
				Tomatic.formatName(name)
			);
		};
		var extensions = Tomatic.grid().extensions || {};
		return m('.extensions', [
			Object.keys(extensions).sort().map(pickCell),
			args.nobodyPickable ? pickCell('ningu') : [],
		]);
	},
};

var WeekList = {
	controller: function(parentcontroller) {
		var controller = {
			model: this,
			parent: parentcontroller,
			setCurrent: function(week) {
				Tomatic.requestGrid(week);
			},
		};
		return controller;
	},
	view: function(c) {
		return m('.weeks',
			Tomatic.weeks().map(function(week){
				var current = Tomatic.currentWeek() === week ? '.current':'';
				return m('.week'+current, {
					onclick: function() {
						c.setCurrent(week);
					}
				}, "Setmana del "+week);
		}));
	}
};
const ButtonIcon = function(msvg) {
	return m.component(IconButton, {
		icon: {
			msvg: msvg
		},
		class: 'colored',
	});
};

const toolbarRow = function(title) {
	return [
		ButtonIcon(iconMenu),
		m('span.flex', title),
		ButtonIcon(iconMore)
	];
}


var TomaticApp = TomaticApp || {};

TomaticApp.controller = function(model, args) {
	args = args || {};
	var controller = {
		currentTab: m.prop('Graelles'),
	};
	return controller;
};

TomaticApp.view = function(c) {
	var grid = Tomatic.grid();
	return [
		m('style',
			Object.keys(grid.colors||{}).map(function(name) {
				let color = '#'+grid.colors[name];
				let darker = '#'+luminance(color, -0.3);
				return (
					'.'+name+', .graella .'+name+' {\n' +
					'  background-color: '+color+';\n' +
					'  border-color: '+darker+';\n' +
					'  border-width: 2pt;\n'+
					'}\n'+
					'.pe-dark-theme .'+name+', .pe-dark-theme .graella .'+name+' {\n' +
					'  background-color: '+darker+';\n' +
					'  border-color: '+color+';\n' +
					'  border-width: 2pt;\n'+
					'}\n');
			})
		),
		m.component(HeaderPanel, {
			mode: 'waterfall-tall',
			//condenses: true, // condense: 
			//noReveal: true, // reveal: remove header when scroll down
			fixed: true,
			keepCondensedHeader: true,
			//animated: true,
			//disolve: true,
			headerHeight: 10,
			class: 'pe-header-panel--fit background-tomatic',
			header: {
				toolbar: {
					class: 'pe-toolbar--tabs.flex',
					topBar: toolbarRow('Tomàtic - Som Energia'),
					bottomBar: m('.tabArea.hasToolbar', [
						m.component(Tabs, {
							buttons: applicationPages,
							centered: true,
							activeSelected: true,
							getState: function(state) {
								c.currentTab(state.data.label);
							}
						})
					]),
				},
			},
			content: [
		c.currentTab()==='Centraleta' && [
			Todo([
				m('b','Sense cap efecte fins que tinguem la centraleta.'),
				" Aqui podeu veure les línies que reben trucades en cada moment, ",
				"podreu també pausar-les o afegir-ne de més. ",
				]),
			m('h2[style=text-align:center]', "Linies en cua"),
			m.component(QueueWidget, c),
		] || [],
		c.currentTab()==='Graelles' && [
			m('.layout.vertical', [
				m.component(WeekList, c),
				m('.layout.end-justified', [
					m.component(Uploader, {
						label: 'Puja Nova Graella',
						url: 'api/graella',
					}),
				]),
			]),
			m('.layout.center-center.wrap', Grid(grid)),
		] || [],
		c.currentTab()==='Graelles' && [
			Extensions(grid.otherextensions),
			m('.layout.around-justified.wrap', [
				Forwardings(),
				Changelog(grid),
				Penalties(grid),
			]),
		] || [],
		c.currentTab() === 'Persones' && [
			Todo("Permetre modificar la configuració personal de cadascú: "+
				"Color, taula, extensió, indisponibilitats..."),
			Persons(grid.extensions),
		] || [],
		c.currentTab() == 'Trucada' && [
			Todo(
				"Aquí es podrà veure informació de l'ERP sobre la trucada entrant"),
		] || [],
		m('#snackbar',m.component(SnackBar)),
		m.component(Dialog),
		]}
		),
	];
};

var editPerson = function(name) {
	Tomatic.editedPerson(name);
	var data = {
		newone: (name?true:false),
		name: name,
		formatName: Tomatic.formatName(name),
		color: Tomatic.grid().colors[name],
		extensio: Tomatic.grid().extensions[name],
		taula: Tomatic.grid().tables[name],
	};
	Dialog.show({
		title: 'Edita dades de la persona',
		body: [
			"TODO: Els canvis encara no són permanents",
			PersonEditor(Tomatic.editedPerson),
		],
		footer: [
			m.component(Button, {
				label: "Ok",
				events: {
					onclick: function() {
						// TODO: save
						Dialog.hide('PersonEditor');
					},
				},
			}),
			m.component(Button, {
				label: "Cancel·la",
				events: {
					onclick: function() {
						Dialog.hide('PersonEditor');
					},
				},
			}),
		],
	},'PersonEditor');
};

var PersonEditor = function(name) {
	var taulaLabel = function(n) {
		var companys = Tomatic.peopleInTable(n)
			.filter(function(item) {
				return item!==name();})
			.map(function(item) {
				return Tomatic.formatName(item);})
			.join(', ')
			;
		return "Taula "+n+": amb "+companys;
	};
	return m('.personEditor', [
		m.component(Tabs, {
			buttons: [
				{
					label: 'Info',
					icon: { msvg: iconMenu },
				},
				{
					label: 'Indis',
					icon: { msvg: iconMenu },
				},
			],
		}),
		m.component(Textfield, {
			label: 'Identificador',
			floatingLabel: true,
			pattern: '[a-z]{2,10}$',
			value: name,
			help: 'Identificador que es fa servir internament.',
			error: 'De 3 a 10 carácters. Només lletres en minúscules.',
			required: true
		}),
		m.component(Textfield, {
			label: 'Nom mostrat',
			floatingLabel: true,
			value: function() {return Tomatic.formatName(name());},
			help: 'Nom amb accents, majúscules...',
			required: true
		}),
		m.component(Textfield, {
			label: 'Extensio',
			type: 'number',
			pattern: '[0-9]{0,4}$',
			floatingLabel: true,
			value: function() {return Tomatic.grid().extensions[name()];},
			help: 'Extensió del telèfon',
			focusHelp: true,
		}),
		m('.pe-textfield.pe-textfield--floating-label.pe-textfield--hide-clear.pe-textfield--dirty', [
			m('.pe-textfield__input-area', [
				m('label.pe-textfield__label', 'Taula'),
				m('select.pe-textfield__input', {
					value: function() {
						var result = Tomatic.grid().tables[name()];
						if (result===undefined) { result = ''; }
						console.log("select value", result, name());
						return ''+result;
					}(),
					onchange: function(ev) {
						var eventValue = ev.target.value;
						console.log('select onchange',eventValue, name());
						if (eventValue==='') {
							eventValue=99;
						}
						Tomatic.grid().tables[name()]=parseInt(eventValue);
					}
				}, [
					m('option', {value: ''}, "Sense taula"),
					[0,1,2,3,4,5,6,7].map(function(n) {
						return m('option', {value: ''+n }, taulaLabel(n));
					}),
					m('option', {value: '8'}, "Taula nova"),
				]),
			]),
		]),
		m('.pe-textfield.pe-textfield--floating-label.pe-textfield--hide-clear.pe-textfield--dirty', [
			m('.pe-textfield__input-area', [
				m('label.pe-textfield__label', 'Color'),
				m.component(RgbEditor, {
					value: function() {
						return Tomatic.grid().colors[name()];
					},
					onEdit: function(rgb) {
						Tomatic.grid().colors[name()]=rgb;
					},
				}),
			]),
		]),
	]);
};

var Grid = function(grid) {
	var editCell = function(day, houri, turni) {
		var setPerson = function(name) {
			Tomatic.editCell(day, houri, turni, name)
			Dialog.hide('GridCellEditor');
		};
		var oldPerson = Tomatic.cell(day,houri,turni);
		Dialog.show({
			title: 'Edita posició de la graella',
			body: [
				Tomatic.weekday(day) +' a les '+
					Tomatic.grid().hours[houri] +
					', línia '+ (turni+1) +
					', la feia ',
				m('span.extension.'+oldPerson, Tomatic.formatName(oldPerson)),
				' qui ho ha de fer?',
				m.component(PersonPicker, {
					id:'GridCellEditor',
					onpick: setPerson,
					nobodyPickable: true,
				}),
			],
			footer: [
				m.component(Button, {
					label: "Cancel·la",
					events: {
						onclick: function() {
							Dialog.hide('GridCellEditor');
						},
					},
				}),
			],
		},'GridCellEditor');
	};
	var cell = function(day, houri, turni) {
		var name = Tomatic.cell(day,houri,turni);
		return m('td', {
			class: name||'ningu',
			onclick: function(ev) {
				editCell(day, houri, turni);
				ev.preventDefault();
			}
		}, [
			Tomatic.formatName(name),
			Tomatic.grid().extensions[name]?
				m('.tooltip', Tomatic.grid().extensions[name]):
				[],
			m.component(Ripple),
		]);
	};
 	return [
		(grid.days||[]).map(function(day, dayi) {
			return m('.graella', m('table', [
				m('tr', [
					m('td'),
					m('th', {colspan:grid.turns.length}, Tomatic.weekday(day)),
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
	];
};

var Persons = function(extensions) {
	return [
		m('.extensions',
			Object.keys(extensions || {}).sort().map(function(name) {
				return m('.extension', {
					class: name,
					onclick: function() {
						editPerson(name);
					},
				}, [
					Tomatic.formatName(name),
					m('br'),
					Tomatic.grid().extensions[name],
					m.component(Ripple),
				]);
			})
		),
	];
};
var Extensions = function(extensions) {
	return [
		m('.extensions',
			Object.keys(extensions || {}).sort().map(function(name) {
				return m('.extension', {class: name}, [
					Tomatic.formatName(name),
					m('br'),
					extensions[name],
				]);
			})
		),
	];
};
var Forwardings = function() {
	return m('.graella', [
		m('h5', 'Codis desviaments'),
		m('ul.codes', [
			m('li','*60 Immediat'),
			m('li','*63 Ocupat o no responem'),
			m('li','*64 Treure desviaments'),
			m('li','*90 Marcar número'),
		]),
	]);
};
var Changelog = function(grid) {
	return m('.graella', [
		m('h5', 'Darrers canvis'),
		m('ul.changelog', [
			grid.log?[]: m('li', 'Cap canvi registrat'),
			(grid.log || []).slice(-5).reverse().map(function(change) {
				return m('li',change);
			}),
			(grid.log || []).length > 5 ?  m('li', m.trust("&hellip;")) : [],
		]),
	]);
};
var Penalties = function(grid) {
	return m('.graella', [
		m('h5', 'Penalitzacions (', grid.cost || 0, ' punts)'),
		m('ul.penalties', [
			grid.penalties?[]: m('li', 'La graella no te penalitzacions'),
			(grid.penalties || []).map(function(penalty) {
				return m('li',penalty[0],': ',penalty[1]);
			}),
		]),
	]);
};


window.onload = function() {
	Tomatic.init();
	m.mount(document.getElementById("tomatic"), TomaticApp);
};

