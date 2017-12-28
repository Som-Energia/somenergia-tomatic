'use strict';
var m = require('mithril');
var jsyaml = require('js-yaml');
var Layout = require('polythene/layout/theme/theme');
var SnackBar = require('polythene/notification/snackbar');
var Button = require('polythene/button/button');
var Dialog = require('polythene/dialog/dialog');
var Checkbox = require('polythene/checkbox/checkbox');
var List = require('polythene/list/list');
var ListTile = require('polythene/list-tile/list-tile');
var Ripple = require('polythene/ripple/ripple');
var Card = require('polythene/card/card');
var HeaderPanel = require('polythene/header-panel/header-panel');
var IconButton = require('polythene/icon-button/icon-button');
var Icon = require('polythene/icon/icon');
var Tabs = require('polythene/tabs/tabs');
var Textfield = require('polythene/textfield/textfield');

var iconMenu = require('mmsvg/google/msvg/navigation/menu');
var iconMore = require('mmsvg/google/msvg/navigation/more-vert');
var iconEdit = require('mmsvg/google/msvg/editor/mode-edit');
var iconPalette = require('mmsvg/google/msvg/image/palette');
var iconDate =  require('mmsvg/google/msvg/action/date-range');
var iconDelete =  require('mmsvg/google/msvg/action/delete');
var iconPlus =  require('mmsvg/templarian/msvg/plus');

var RgbEditor = require('./components/rgbeditor');
var Uploader = require('./components/uploader');
var luminance = require('./components/colorutils').luminance;

var theme = require('polythene/theme/theme');
var customStyle = require('./style.styl');

var Tomatic = {
};

Tomatic.queue = m.prop([]);
Tomatic.persons = m.prop({});
Tomatic.init = function() {
	this.requestWeeks();
	this.requestQueue();
	this.requestPersons();
};
Tomatic.requestPersons = function() {
	m.request({
		method: 'GET',
		url: '/api/persons',
		deserialize: jsyaml.load,
	}).then(function(response){
		if (response.persons!==undefined) {
			Tomatic.persons(response.persons);
		}
	});
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
		delete data.colors;
		delete data.names;
		delete data.extensions;
		delete data.tables; // TODO: This one was never added
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
	return (Tomatic.persons().names||{})[name] || titleCase(name);
};
Tomatic.extension = function(name) {
	return Tomatic.formatName(name) + ": "
		+ ((Tomatic.persons().extensions||{})[name] || "???");
};
Tomatic.table = function(name) {
	var tables = Tomatic.persons().tables;
	if (!tables) { Tomatic.persons().tables={}; } // TODO: Move that anywhere else
	var table = Tomatic.persons().tables[name];
	if (table == undefined) { return 99; }
	return table;
};
Tomatic.peopleInTable = function(table) {
	var tables = Tomatic.persons().tables || {};
	var result = Object.keys(tables).filter(function(k) {
		return Tomatic.table(k)===table;
		});
	return result;
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
Tomatic.setPersonData = function (name, data) {
	if (name===undefined) {
		name = data.name;
	}
	var postdata = {};

	for (var key in data) {
		var value = data[key];
		switch (key) {
		case 'formatName':
			delete Tomatic.persons().names[name];
			var formatName = Tomatic.formatName(name);
			if (formatName!==value) {
				postdata.name = value;
			}
			break;
		case 'extension':
			postdata.extension = value;
			break;
		case 'table':
			postdata.table = parseInt(value,10);
			break;
		case 'color':
			postdata.color = value;
			break;
		}
	}
	console.log("posting",postdata);
	m.request({
		method: 'POST',
		url: '/api/person/'+name,
		data: postdata,
		deserialize: jsyaml.load,
	})
	.then( function(data) {
		Tomatic.requestPersons();
	}, function(error) {
		console.log(error);
		Tomatic.error("Problemes editant la persona: "+
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
		var weeks = newWeeklist.weeks.sort().reverse();
		Tomatic.weeks(weeks);
		if (Tomatic.currentWeek()===undefined) {
			var expirationms = 1000*60*60*(24*4 + 18);
			var oldestWeek = new Date(new Date().getTime()-expirationms);
			var current = undefined;
			for (var i in weeks) {
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
	console.log("error: ", message);
	SnackBar.show({
		containerSelector: '#snackbar',
		title: message,
		class: 'error',
	});
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
		var extensions = Tomatic.persons().extensions || {};
		return m('.extensions', [
			Object.keys(extensions).sort().map(pickCell),
			args.nobodyPickable ? pickCell('ningu') : [],
		]);
	},
};

var WeekList = {
	controller: function() {
		var controller = {
			model: this,
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


var BusyList = {
	view: function(ctrl, attrs) {
		return m('',[
			m.component(List, {
				header: {
					title: m('.layout.justified.center', [
						attrs.title,
						m.component(IconButton, {
							icon: { msvg: iconPlus, },
							compact: true,
							wash: true,
							class: 'colored',
							events: {
								onclick: function () {
									alert("Adding new");
									// TODO: implement dialog
									attrs.entries.push({
										date: '2017-12-20',
										reason: 'No reason',
										optional: false,
										slot: '1100',
									});
								},
							}
						}),
					]),
				},
				//compact: true,
				tiles: attrs.entries.map(function(entry, index) {
					var slots = Array.from(entry.slot).map(function(e) {
						return m.trust(e-0?'&#x2610;':'&#x2612;');
					});
					var weekdays = {
						dl: 'Dilluns',
						dm: 'Dimarts',
						dx: 'Dimecres',
						dj: 'Dijous',
						dv: 'Divendres',
					};
					var day = entry.date || weekdays[entry.weekday] || 'Tots';

					return m.component(ListTile, {
						front: m('.optionallabel',
							entry.optional?'Opcional':''),
						title: m('.layout.justified', [
							day,
							m('.slots',slots)
						]),
						subtitle: entry.reason,
						secondary: {
							content: m.component(IconButton, {
								icon: { msvg: iconDelete },
								compact: true,
								wash: true,
								class: 'colored',
								events: {
									onclick: function() {
										attrs.entries.splice(index, 1);
										console.log(attrs.entries);
									},
								},
							}),
						},
						events: {
							onclick: function() {
								alert("edit");
							},
						},
					});
				}),
				borders: true,
				hoverable: true,
			}),
		]);
	},
};

Tomatic.retrieveBusyData = function(name, callback) {
	console.log("retrieving", name);
	setTimeout(function () {
		callback( {
			'oneshot': [
				{
					'date': '2013-06-23',
					'slot': '0011',
					'optional': true,
					'reason': 'motivo 0',
				},
				{
					'date': '2013-12-23',
					'slot': '0110',
					'optional': false,
					'reason': 'motivo 1',
				},
				{
					'date': '2017-02-23',
					'slot': '1100',
					'optional': true,
					'reason': 'motivo 2',
				},
				{
					'date': '2019-12-25',
					'slot': '1111',
					'optional': false,
					'reason': 'me quedo en casa rascandome los gatos',
				},
			],
			'weekly': [
				{
					'weekday': 'dm',
					'slot': '1111',
					'optional': false,
					'reason': 'motivo 3',
				},
				{
					'weekday': null,
					'slot': '0011',
					'optional': false,
					'reason': 'me quedo en casa rascandome los gatos',
				},
			],
		});
	},1000);
};


var editAvailabilities = function(name) {
	Dialog.show({
		title: 'Obtenint indisponibilitats...',
	}, 'BusyRetriever');

	Tomatic.retrieveBusyData(name, function(data) {
		Dialog.hide('BusyRetriever');
		Dialog.show({
			title: 'Edita indisponibilitats',
			body: [
				"TODO: Les dades encara son de MENTIDA!",
				m('.busyeditor', [
					m.component(BusyList, {
						title: 'Puntuals',
						entries: data.oneshot
					}),
					m.component(BusyList, {
						title: 'Setmanals',
						entries: data.weekly,
					}),
				]),
			],
			footer: [
				m.component(Button, {
					label: "Ok",
					events: {
						onclick: function() {
							// TODO: Send new busy data to the API
							//Tomatic.setBusyData(name, data);
							console.log("Final data:\n",data);
							Dialog.hide('BusyEditor');
						},
					},
				}),
				m.component(Button, {
					label: "Cancel·la",
					events: {
						onclick: function() {
							Dialog.hide('BusyEditor');
						},
					},
				}),
			],
		},'BusyEditor');
		m.redraw();
	});
};

var editPerson = function(name) {
	var taulaLabel = function(n) {
		var companys = Tomatic.peopleInTable(n)
			.filter(function(item) {
				return item!==name;})
			.map(function(item) {
				return Tomatic.formatName(item);})
			.join(', ')
			;
		if (!companys) { companys = "ningú més"; }
		return "Taula "+n+": amb "+companys;
	};
	function getDataFromTomatic(name) {
		return {
			newone: (name===undefined?true:false),
			name: name,
			formatName: Tomatic.formatName(name),
			color: Tomatic.persons().colors[name],
			extension: Tomatic.persons().extensions[name],
			table: Tomatic.table(name),
		};
	};
	function setDataOnTomatic(name, data) {
		var old = getDataFromTomatic(name);
		var changed = {};
		for (var k in old) {
			if (old[k]!==data[k]) {
				changed[k]=data[k];
			}
		}
		console.log('setDataOnTomatic', name, changed);
		Tomatic.setPersonData(name, data);
	};
    function maxValue(object) {
        var keys = Object.keys(object);
        var values = keys.map(function(key) { return object[key]; })
        return Math.max.apply(null, values);
    }
    function range(n) {
        return Array.apply(null, Array(n)).map(function (_, i) {return i;});
    }

	var data = getDataFromTomatic(name);
	data.tables = {};
	var tablesToFill = range(maxValue(Tomatic.persons().tables)+2);
	tablesToFill.map(function(n) {
		data.tables[n] = taulaLabel(n);
	});
	Dialog.show({
		title: 'Edita dades de la persona',
		body: [
			m.component(PersonEditor, data),
		],
		footer: [
			m.component(Button, {
				label: "Ok",
				events: {
					onclick: function() {
						setDataOnTomatic(name, data);
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

var PersonEditor = {};
PersonEditor.view = function(ctrl, attrs) {
	ctrl.name = attrs.name;
	return m('.personEditor', [
		m.component(Textfield, {
			label: 'Identificador',
			floatingLabel: true,
			pattern: '[a-z]{3,10}$',
			help: 'Identificador que es fa servir internament.',
			error: 'De 3 a 10 carácters. Només lletres en minúscules.',
			required: true,
			disabled: !attrs.newone,
			value: attrs.name || '',
			events: {
				onchange: function(ev) {
					attrs.name=ev.target.value;
				},
			},
		}),
		m.component(Textfield, {
			label: 'Nom mostrat',
			floatingLabel: true,
			help: 'Nom amb accents, majúscules...',
			required: true,
			value: function() {
				return attrs.formatName;
			},
			events: {
				onchange: function(ev) {
					attrs.formatName=ev.target.value;
				},
			},
		}),
		m.component(Textfield, {
			label: 'Extensio',
			type: 'number',
			pattern: '[0-9]{0,4}$',
			floatingLabel: true,
			help: 'Extensió del telèfon',
			required: true,
			value: function() {
				return attrs.extension;
			},
			events: {
				onchange: function(ev) {
					attrs.extension=ev.target.value;
				},
			},
		}),
		m('.pe-textfield.pe-textfield--floating-label.pe-textfield--hide-clear.pe-textfield--dirty', [
			m('.pe-textfield__input-area', [
				m('label.pe-textfield__label', 'Taula'),
				m('select.pe-textfield__input', {
					value: ''+attrs.table==='-1'?'':attrs.table,
					onchange: function(ev) {
						var eventValue = ev.target.value;
						console.log("onchange", eventValue);
						if (eventValue==='') { eventValue='-1'; }
						attrs.table=eventValue;
					},
				}, [
					m('option', {value: ''}, "Sense taula"),
					Object.keys(attrs.tables).map(function(value) {
						return m('option', {
							value: value,
							selected: value == attrs.table,
						}, attrs.tables[value]);
					}),
				]),
			]),
		]),
		m('.pe-textfield.pe-textfield--floating-label.pe-textfield--hide-clear.pe-textfield--dirty', [
			m('.pe-textfield__input-area', [
				m('label.pe-textfield__label', 'Color'),
				m.component(RgbEditor, {
					value: function() {
						return attrs.color;
					},
					onEdit: function(rgb) {
						attrs.color = rgb;
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
			Tomatic.persons().extensions[name]?
				m('.tooltip', Tomatic.persons().extensions[name]):
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
		m('.extensions', [
			Object.keys(extensions || {}).sort().map(function(name) {
				return m('.extension', {
					class: name,
					_onclick: function() {
						editPerson(name);
					},
				}, [
					Tomatic.formatName(name),
					m('br'),
					Tomatic.persons().extensions[name],
					m('.tooltip', [
						m.component(IconButton, {
							icon: { msvg: iconDate },
							compact: true,
							wash: true,
							class: 'colored',
							events: {
							onclick: function() { editAvailabilities(name); },
							},
						}),
						m.component(IconButton, {
							icon: { msvg: iconEdit },
							compact: true,
							wash: true,
							class: 'colored',
							events: {
							onclick: function() { editPerson(name); },
							},
						}),
					]),
					//m.component(Ripple),
				]);
			}),
			m('.extension.add', {
				onclick: function() {
					editPerson();
				},
			}, [
				'nova', m('br'), 'persona',
			]),
		]),
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

var GridsPage = {
    view: function() {
        var grid = Tomatic.grid();
        return m('',[
			m('.layout.vertical', [
				m.component(WeekList),
				m('.layout.end-justified', [
					m.component(Uploader, {
						name: 'yaml',
						label: 'Puja Nova Graella',
						url: 'api/graella',
						onupload: function(result) {
							Tomatic.init();
						},
						onerror: function(error) {
							console.log("Upload error:", error);
							Tomatic.error("Upload error: " + error.error);
						},
					}),
				]),
			]),
			m('.layout.center-center.wrap', Grid(grid)),
			Extensions(grid.otherextensions),
			m('.layout.around-justified.wrap', [
				Forwardings(),
				Changelog(grid),
				Penalties(grid),
			]),
        ]);
    },
};

var PbxPage = {
    view: function() {
        return m('', [
			Todo([
				m('b','Sense cap efecte fins que tinguem la centraleta.'),
				" Aqui podeu veure les línies que reben trucades en cada moment, ",
				"podreu també pausar-les o afegir-ne de més. ",
				]),
			m('h2[style=text-align:center]', "Linies en cua"),
			m.component(QueueWidget),
        ]);
    },
};

var PersonsPage = {
    view: function() {
        return m('', [
			Todo("Permetre modificar la configuració personal de cadascú: "+
				"Color, taula, extensió, indisponibilitats..."),
			Persons(Tomatic.persons().extensions),
        ]);
    },
};

var CallInfoPage = {
    view: function() {
        return m('',[
			Todo(
				"Aquí es podrà veure informació de l'ERP sobre la trucada entrant"
            ),
        ]);
    },
};

var PersonStyles = function() {
	var persons = Tomatic.persons();
    return m('style',
        Object.keys(persons.colors||{}).map(function(name) {
            var color = '#'+persons.colors[name];
            var darker = '#'+luminance(color, -0.3);
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
    );
};

const applicationPages = [
	"Graelles",
	"Centraleta",
	"Persones",
	"Trucada",
	];

var tabs = applicationPages.map(function(name) {
    return {
        label: name,
        url: {
            config: m.route,
            href: '!/'+name
        },
    };
});
const indexForRoute = function(route) {
    return tabs.reduce(function(previousValue, tab, index) {
        if (route === tab.url.href) {
            return index;
        } else {
            return previousValue;
        }
    }, 0);
};

var Page = function(content) {
    var currentTabIndex = indexForRoute(m.route());


	return m.component(HeaderPanel, {
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
                        buttons: tabs,
                        centered: true,
                        activeSelected: true,
                        //hideIndicator: true,
                        selectedTab: currentTabIndex,
                    })
                ]),
            },
        },
        content: [
            content,
            m('#snackbar',m.component(SnackBar)),
            m.component(Dialog),
        ],
    });
};


var TomaticApp = {}
TomaticApp.controller = function() {
    return {
    };
}
TomaticApp.view = function(c) {
    var pages = {
        'Graelles': GridsPage,
        'Centraleta': PbxPage,
        'Persones': PersonsPage,
        'Trucada': CallInfoPage,
    };
    var currentTabIndex = indexForRoute(m.route());
    var current = pages[tabs[currentTabIndex].label];
    return [
        PersonStyles(),
        Page(m.component(current)),
    ];
};



window.onload = function() {
	Tomatic.init();
    m.route.mode = 'hash';
    m.redraw.strategy('diff');
	m.mount(document.getElementById("tomatic"), TomaticApp);
/*  // Not working
	m.route(document.getElementById("tomatic"), '/Graelles', {
        '/Graelles': TomaticApp,
        '/Centraleta': TomaticApp,
        '/Persones': TomaticApp,
        '/Trucada': TomaticApp,
    });
*/
};
// vim: noet ts=4 sw=4
