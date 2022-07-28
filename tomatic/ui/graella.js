'use strict';
var m = require('mithril');

m.prop = require('mithril/stream');

var Snackbar = require('polythene-mithril-snackbar').Snackbar;
var Dialog = require('polythene-mithril-dialog').Dialog;
var Card = require('polythene-mithril-card').Card;
var Tabs = require('polythene-mithril-tabs').Tabs;

var iconMenu = require('mmsvg/google/msvg/navigation/menu');
var iconMore = require('mmsvg/google/msvg/navigation/more-vert');

var Tomatic = require('./components/tomatic');
var QueueMonitor = require('./components/queuemonitor');
var luminance = require('./components/colorutils').luminance;
var contrast = require('./components/colorutils').contrast;
var Login = require('./components/login');
var Persons = require('./components/persons');
var TimeTablePage = require('./components/timetablepage');
var MenuButton = require('./components/menubutton');

var css = require('polythene-css');
var customStyle = require('./style.styl');

var CallInfoPage = require('./components/callinfopage');

css.addLayoutStyles();
css.addTypography();

var kumato=JSON.parse(localStorage.getItem('kumato', false)); // Dark interface

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

const scriptLauncherBase = 'http://tomatic.somenergia.lan:5000';
const menuOptions = function() { return [{
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


var PbxPage = {
    view: function() {
        return m('', [
			Doc(m('',
				"Visualitza les línies que estan actualment rebent trucades. "+
				"Feu click al damunt per pausar-les o al signe '+' per afegir-ne")
			),
			m('h2[style=text-align:center]', "Linies en cua"),
			m(QueueMonitor),
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
				activeSelected: true,
				selectedTab: currentTabIndex,
			}),
		]),
		vnode.attrs.content,
		m('#snackbar',m(Snackbar)),
		m(Dialog),
	]);
};


var TomaticApp = {}
TomaticApp.view = function(vnode) {
	console.log("Page: ", m.route.get());
    return m(''
			+(kumato?'.pe-dark-tone':'')
			+('.variant-'+Tomatic.variant)
			
		,[
        PersonStyles(),
        m(Page, {content: vnode.children}),
    ]);
};



window.onload = function() {
	Tomatic.init();
    //m.redraw.strategy('diff');
	var element = document.getElementById("tomatic");
	m.route(element, '/Graelles', {
        '/Graelles': {render: function() { return m(TomaticApp, m(TimeTablePage)) }},
        '/Centraleta': {render: function() { return m(TomaticApp, m(PbxPage)) }},
        '/Persones': {render: function() { return m(TomaticApp, m(PersonsPage)) }},
        '/Trucada': {render: function() { return m(TomaticApp, m(CallInfoPage)) }},
    });
};
// vim: noet ts=4 sw=4
