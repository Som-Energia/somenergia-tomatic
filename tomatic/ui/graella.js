'use strict';
var m = require('mithril');

m.prop = require('mithril/stream');

var Snackbar = require('polythene-mithril-snackbar').Snackbar;
var Button = require('polythene-mithril-button').Button;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Card = require('polythene-mithril-card').Card;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var List = require('polythene-mithril-list').List;
var Shadow = require('polythene-mithril-shadow').Shadow;
var Menu = require('polythene-mithril-menu').Menu;
var Ripple = require('polythene-mithril-ripple').Ripple;
var IconButton = require('polythene-mithril-icon-button').IconButton;
var Tabs = require('polythene-mithril-tabs').Tabs;
var Textfield = require('polythene-mithril-textfield').TextField;


var iconMenu = require('mmsvg/google/msvg/navigation/menu');
var iconMore = require('mmsvg/google/msvg/navigation/more-vert');
var iconEdit = require('mmsvg/google/msvg/editor/mode-edit');
var iconPalette = require('mmsvg/google/msvg/image/palette');
var iconDate =  require('mmsvg/google/msvg/action/date-range');

var Tomatic = require('./components/tomatic');
var Select = require('./components/select');
var RgbEditor = require('./components/rgbeditor');
var Uploader = require('./components/uploader');
var luminance = require('./components/colorutils').luminance;
var contrast = require('./components/colorutils').contrast;
var editAvailabilities = require('./components/busyeditor');
var Login = require('./components/login');

var css = require('polythene-css');
var customStyle = require('./style.styl');

var CallInfoPage = require('./components/callinfopage');
var getCookie = require('./components/utils').getCookie;

css.addLayoutStyles();
css.addTypography();

var kumato=JSON.parse(localStorage.getItem('kumato', false)); // Dark interface

var Todo = function(message) {
	return m(Card, {
		content: [{
			primary: {
				title: 'TODO',
				subtitle: message,
			},
		}],
	});
};

var Doc = function(message) {
	return m(Card, {
		content: [{
			primary: {
				title: "Info",
				subtitle: message,
			},
		}],
	});
};

var QueueWidget = {
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
var PersonPicker = {
	oninit: function(vnode) {
		vnode.state.onpick = vnode.attrs.onpick;
		vnode.state.nobodyPickable = vnode.attrs.nobodyPickable;
		vnode.state.person = m.prop(undefined);
		vnode.state.picked = function(name, ev) {
			vnode.state.person(name);
			if (vnode.attrs.onpick) {
				vnode.attrs.onpick(name);
			}
		};
	},
	view: function(vnode) {
		var pickCell = function(name) {
			return m('.extension', {
				className: name,
				onclick: vnode.state.picked.bind(vnode,name),
				},
				Tomatic.formatName(name)
			);
		};
		var extensions = Tomatic.persons().extensions || {};
		return m('.extensions', [
			Object.keys(extensions).sort().map(pickCell),
			vnode.attrs.nobodyPickable ? pickCell('ningu') : [],
		]);
	},
};

var WeekList = {
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
		}));
	}
};

const scriptLauncherBase = 'http://tomatic.somenergia.lan:5000';
const menuOptions = function() { return [{
	title: "Genera càrregues setmanals",
	action: function() {
		location.href = scriptLauncherBase + "/runner/carregues";
	},
},{
	title: "Planificador de Graelles",
	action: function() {
		location.href = "/api/planner/";
	},
},{
	title: "Estadístiques de trucades",
	action: function() {
		location.href = scriptLauncherBase + "/runner/statshistory";
	},
},{
	title: "En Tomàtic diu...",
	action: function() {
		location.href = scriptLauncherBase + "/runner/says";
	},
},{
	title: "Reomple el torn que toca a la cua",
	action: function() {
		location.href = scriptLauncherBase + "/runner/reloadqueue";
	},
},{
	title: "Anotacions: Actualitza categories",
	action: function() {
		CallInfoPage.settingsDialog()
	},
},{
	title: "Altres scripts de Centraleta",
	action: function() {
		location.href = scriptLauncherBase;
	},
},{
	title: "Kumato mode",
	action: function() {
		kumato = !kumato
		localStorage.kumato = kumato;
	},
}]};

const toolbarRow = function(title) {
	return m('.pe-dark-tone.pe-toolbar.flex.layout',[
		m(MenuButton, {
			icon: iconMenu,
			origin: 'top-left',
		}),
		m('.flex', title),
		Login.identification(),
		m(MenuButton, {
			id: 'right-menu',
			icon: iconMore,
			origin: 'top-right',
			options: menuOptions(),
		}),
	]);
}



const MenuContent = function(options) {
	return m(List, {
		compact: true,
		tiles: options.map(function(item) {
			return m(ListTile, {
				title: item.title,
				ink: true,
				hoverable: true,
				className: 'colored',
				disabled: item.disabled,
				events: {
					onclick: item.action,
				},
			});
		}),
	});
};

const MenuButton = {
	oninit: function(vnode) {
		vnode.state.shown = false;
		vnode.attrs.id = vnode.attrs.id || 'the_menu'
	},
	view: function(vnode) {
		var attrs = vnode.attrs;
		return m("", {
			style: {
				position: 'relative',
			}
		},[
			m(Shadow),
			m(Menu, {
				target: "#" + attrs.id,
				origin: attrs.origin || false,
				size: 5,
				offset: 30,
				show: vnode.state.shown,
				didHide: function() {
					vnode.state.shown = false;
				},
				content: MenuContent(attrs.options || []),
			}),
			m(IconButton, {
				icon: {
					svg: attrs.icon || iconMore
				},
				className: 'colored',
				id: attrs.id,
				events: {
					onclick: function(ev) {
						vnode.state.shown = true;
					},
				},
			}),
		])
	},

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
			email: Tomatic.persons().emails[name],
			erpuser: Tomatic.persons().erpusers[name],
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
		if (keys.length === 0) return 0;
		var values = keys.map(function(key) { return object[key]; });
		return Math.max.apply(null, values);
	}
	function range(n) {
		if (n==0) return Array();
		return Array.apply(null, Array(n)).map(function (_, i) {return i;});
	}

	var data = getDataFromTomatic(name);
	data.tables = {};
	var tablesToFill = range(maxValue(Tomatic.persons().tables)+2);
	tablesToFill.map(function(n) {
		data.tables[n] = taulaLabel(n);
	});
	Dialog.show(function() { return {
		title: 'Edita dades de la persona '+Tomatic.formatName(name),
		backdrop: true,
		body: [
			m(PersonEditor, data),
		],
		footerButtons: [
			m(Button, {
				label: "Accepta",
				events: {
					onclick: function() {
						setDataOnTomatic(name, data);
						Dialog.hide({id: 'PersonEditor'});
					},
				},
			}),
			m(Button, {
				label: "Cancel·la",
				events: {
					onclick: function() {
						Dialog.hide({id:'PersonEditor'});
					},
				},
			}),
		],
		didHide: function() {m.redraw();}
	};},{id:'PersonEditor'});
};

var PersonEditor = {};
PersonEditor.view = function(vnode) {
	vnode.state.name = vnode.attrs.name;
	return m('.personEditor', [
		m(Textfield, {
			label: 'Identificador',
			floatingLabel: true,
			pattern: '[a-z]{3,10}$',
			help: 'Identificador que es fa servir internament.',
			error: 'De 3 a 10 carácters. Només lletres en minúscules.',
			required: true,
			disabled: !vnode.attrs.newone,
			value: vnode.attrs.name || '',
			events: {
				oninput: function(ev) {
					ev.target.value = ev.target.value
						.toLowerCase()
						.replace(/[óòôö]/g,'o')
						.replace(/[àáâä]/g,'a')
						.replace(/[íìîï]/g,'i')
						.replace(/[úûûü]/g,'u')
						.replace(/[éèêë]/g,'e')
						.replace(/[ç]/g,'c')
						.replace(/[ñ]/g,'n')
						.replace(/[^a-z]/g,'')
						.slice(0,10);
				},
			},
			onChange: function(state) {
				vnode.attrs.name=state.value;
			},
		}),
		m(Textfield, {
			label: 'Nom mostrat',
			floatingLabel: true,
			help: 'Nom amb accents, majúscules...',
			required: true,
			value: vnode.attrs.formatName,
			onChange: function(state) {
				vnode.attrs.formatName=state.value;
			},
		}),
		m(Textfield, {
			label: 'Correu electrònic',
			floatingLabel: true,
			type: 'email',
			help: 'Correu oficial que tens a Som Energia.',
			error: 'Correu invàlid.',
			required: true,
			value: vnode.attrs.email || '',
			onChange: function(state) {
				vnode.attrs.email=state.value;
			},
		}),
		m(Textfield, {
			label: 'Usuari ERP',
			floatingLabel: true,
			help: 'Usuari amb el que entres a l\'erp.',
			required: true,
			value: vnode.attrs.erpuser || '',
			onChange: function(state) {
				vnode.attrs.erpuser=state.value;
			},
		}),
		m(Textfield, {
			label: 'Extensio',
			type: 'number',
			pattern: '[0-9]{4}$',
			floatingLabel: true,
			help: 'Extensió de telèfon',
			required: true,
			value: vnode.attrs.extension,
			onChange: function(state) {
				vnode.attrs.extension=state.value;
			},
		}),
		m(Select, {
			label: 'Taula',
			value: vnode.attrs.table,
			options: Object.keys(vnode.attrs.tables).reduce(function(d, k) {
				d[k] = vnode.attrs.tables[k];
				return d;
			}, { "-1": "Sense taula" }),
			onChange: function(ev) {
				vnode.attrs.table = ev.target.value;
			},
		}),
		m(
			'.pe-textfield'+
			'.pe-textfield--floating-label'+
			'.pe-textfield--hide-clear'+
			'.pe-textfield--dirty', [
			m('.pe-textfield__input-area', [
				m('label.pe-textfield__label', 'Color'),
				m(RgbEditor, {
					value: vnode.attrs.color || 'ffffff',
					onChange: function(state) {
						vnode.attrs.color = state.value;
					},
				}),
			]),
		]),
	]);
};

var Grid = function(grid) {
	var editCell = function(day, houri, turni) {
		var setPerson = function(name) {
			var myname = Login.myName();
			Tomatic.editCell(day, houri, turni, name, myname)
			Dialog.hide({id:'GridCellEditor'});
		};
		var oldPerson = Tomatic.cell(day,houri,turni);
		Dialog.show({
			id: 'GridCellEditor',
			title: 'Edita posició de la graella',
			backdrop: true,
			body: [
				Tomatic.weekday(day) +' a les '+
					Tomatic.grid().hours[houri] +
					', línia '+ (turni+1) +
					', la feia ',
				m('span.extension.'+oldPerson, Tomatic.formatName(oldPerson)),
				' qui ho ha de fer?',
				m(PersonPicker, {
					id:'GridCellEditor',
					onpick: setPerson,
					nobodyPickable: true,
				}),
			],
			footerButtons: [
				m(Button, {
					label: "Cancel·la",
					events: {
						onclick: function() {
							Dialog.hide({id:'GridCellEditor'});
						},
					},
				}),
			],
		},{id:'GridCellEditor'});
	};
	var cell = function(day, houri, turni) {
		var name = Tomatic.cell(day,houri,turni);
		return m('td', {
			className: name||'ningu',
			onclick: function(ev) {
				if(getCookie("tomaticCookie")===":"){
					Login.askWhoAreYou();
				}
				else {
					editCell(day, houri, turni);
					ev.preventDefault();
				}
			}
		}, [
			Tomatic.formatName(name),
			Tomatic.persons().extensions[name]?
				m('.tooltip', Tomatic.persons().extensions[name]):
				[],
			m(Ripple),
		]);
	};
	if (!grid.turns) {
		return [];
	}
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
					className: name,
					_onclick: function() {
						editPerson(name);
					},
				}, [
					Tomatic.formatName(name),
					m('br'),
					Tomatic.persons().extensions[name],
					m('.tooltip', [
						m(IconButton, {
							icon: { svg: iconDate },
							compact: true,
							wash: true,
							className: 'colored',
							events: {
							onclick: function() { editAvailabilities(name); },
							},
						}),
						m(IconButton, {
							icon: { svg: iconEdit },
							compact: true,
							wash: true,
							className: 'colored',
							events: {
							onclick: function() { editPerson(name); },
							},
						}),
					]),
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
				return m('.extension', {className: name}, [
					Tomatic.formatName(name),
					m('br'),
					extensions[name],
				]);
			})
		),
	];
};
var Changelog = function(grid) {
	return m('.graella', [
		m('h5', 'Darrers canvis'),
		m('ul.changelog', [
			grid.log?[]: m('li', 'Cap canvi registrat'),
			(grid.log || []).slice(0,-1).reverse().map(function(change) {
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

var Overloads = function(grid) {
	return m('.graella', [
		m('h5', 'Sobrecarrega respecte l\'ideal'),
		m('ul.overloads', [
			grid.overload?[]: m('li', 'La graella no te sobrecarregues apuntades'),
			Object.keys(grid.overload || {}).map(function (person) {
				return m('li',person,': ',grid.overload[person]);
			}),
		]),
	]);
};

var GridsPage = {
    view: function() {
        var grid = Tomatic.grid();
        return m('',[
			m('.layout.vertical', [
				m(WeekList),
				m('.layout.end-justified', [
					m(Uploader, {
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
				Changelog(grid),
				Penalties(grid),
				Overloads(grid),
			]),
        ]);
    },
};

var PbxPage = {
    view: function() {
        return m('', [
			Doc(m('',
				"Visualitza les línies que estan actualment rebent trucades. "+
				"Feu click al damunt per pausar-les o al signe '+' per afegir-ne")
			),
			m('h2[style=text-align:center]', "Linies en cua"),
			m(QueueWidget),
        ]);
    },
};

var PersonsPage = {
    view: function() {
        return m('', [
			Doc("Permet modificar la configuració personal de cadascú: "+
				"Color, taula, extensió, indisponibilitats..."),
			Persons(Tomatic.persons().extensions),
        ]);
    },
};


var PersonStyles = function() {
    var persons = Tomatic.persons();
    return m('style',
        Object.keys(persons.colors||{}).map(function(name) {
            var color = '#'+persons.colors[name];
            var darker = '#'+luminance(color, -0.3);
            var linecolor = contrast(persons.colors[name])
            return (
                '.'+name+', .graella .'+name+' {\n' +
                '  background-color: '+color+';\n' +
                '  border-color: '+darker+';\n' +
                '  border-width: 20pt;\n'+
                '  color: '+linecolor+';\n'+
                '}\n'+
                '.pe-dark-theme .'+name+', .pe-dark-theme .graella .'+name+' {\n' +
                '  background-color: '+darker+';\n' +
                '  border-color: '+color+';\n' +
                '  border-width: 2pt;\n'+
                '  color: '+linecolor+';\n'+
                '}\n'
            );
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
		element: m.route.Link,
        url: {
            href: '/'+name
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


var Page = {};
Page.view = function(vnode) {
    var currentTabIndex = indexForRoute(m.route.get());
	return m('', [
		m('.tmt-header', [
			m('.tmt-header__dimmer'),
            toolbarRow('Tomàtic - Som Energia'),
			m(Tabs, {
				tabs: tabs,
				//centered: true,
				activeSelected: true,
				//hideIndicator: true,
				selectedTab: currentTabIndex,
			}),
		]),
		vnode.attrs.content,
		m('#snackbar',m(Snackbar)),
		m(Dialog),
	]);
		
};


var TomaticApp = {}
TomaticApp.view = function() {
    var pages = {
        'Graelles': GridsPage,
        'Centraleta': PbxPage,
        'Persones': PersonsPage,
        'Trucada': CallInfoPage,
    };
	console.log("Page: ", m.route.get());
    var currentTabIndex = indexForRoute(m.route.get());
    var current = m(pages[tabs[currentTabIndex].label]);
    return m(''
			+(kumato?'.pe-dark-tone':'')
			+('.variant-'+Tomatic.variant)
			
		,[
        PersonStyles(),
        m(Page, {content:current}),
    ]);
};



window.onload = function() {
	Tomatic.init();
    //m.redraw.strategy('diff');
	var element = document.getElementById("tomatic");
	m.route(element, '/Graelles', {
        '/Graelles': TomaticApp,
        '/Centraleta': TomaticApp,
        '/Persones': TomaticApp,
        '/Trucada': TomaticApp,
    });
};
// vim: noet ts=4 sw=4