// Busy list editor
module.exports = function() {
var m = require('mithril');
var Dialog = require('polythene-mithril-dialog').Dialog;
var Button = require('polythene-mithril-button').Button;
var List = require('polythene-mithril-list').List;
var ListTile = require('polythene-mithril-list-tile').ListTile;
var Textfield = require('polythene-mithril-textfield').TextField;
var RadioGroup = require('polythene-mithril-radio-group').RadioGroup;
var RadioButton = require('polythene-mithril-radio-button').RadioButton;
var IconButton = require('polythene-mithril-icon-button').IconButton;
var Checkbox = require('polythene-mithril-checkbox').Checkbox;
var DatePicker = require('mithril-datepicker/mithril-datepicker')
var datePickerStyle = require('mithril-datepicker/src/style.css');
var Select = require('./select');
var Tomatic = require('./tomatic')
var iconPlus =  require('mmsvg/templarian/msvg/plus');
var iconDelete =  require('mmsvg/google/msvg/action/delete');

function nextMonday(date) {
	var d = d || new Date();
	d.setDate(d.getDate() + 14 - (6+d.getDay())%7);
	return d.toISOString().substr(0,10);
}


var BusyList = {
	view: function(vnode, attrs) {
		return m('',[
			m(List, {
				header: {
					title: m('.layout.justified.center', [
						vnode.attrs.title,
						m(IconButton, {
							icon: { svg: iconPlus, },
							compact: true,
							wash: true,
							class: 'colored',
							events: {
								onclick: function () {
									var newEntry = {
										weekday: vnode.attrs.isOneShot?undefined:'',
										date: vnode.attrs.isOneShot?nextMonday():undefined,
										reason: '',
										optional: true,
										turns: '0000',
									};
									editAvailability(newEntry, function(entry) {
										vnode.attrs.entries.push(entry);
										vnode.attrs.onChange && vnode.attrs.onChange();
									});
								},
							}
						}),
					]),
				},
				//compact: true,
				tiles: vnode.attrs.entries.map(function(entry, index) {
					var turns = Array.from(entry.turns).map(function(e) {
						return m.trust(e-0?'&#x2612;':'&#x2610;');
					});
					var day = entry.date || Tomatic.weekday(entry.weekday, 'Tots els dies');

					return m(ListTile, {
						front: m('.optionallabel',
							entry.optional?'Opcional':''),
						title: m('.layout.justified', [
							day,
							m('.turns',turns)
						]),
						subtitle: entry.reason,
						secondary: {
							content: m(IconButton, {
								icon: { svg: iconDelete },
								compact: true,
								wash: true,
								class: 'colored',
								events: {
									onclick: function() {
										vnode.attrs.entries.splice(index, 1);
										console.log(vnode.attrs.entries);
										vnode.attrs.onChange && vnode.attrs.onChange();
									},
								},
							}),
						},
						events: {
							onclick: function() {
								editAvailability(entry, function(modifiedEntry) {
									Object.assign(entry, modifiedEntry);
									vnode.attrs.onChange && vnode.attrs.onChange();
								});
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

var BusyEntryEditor = {
	oncreate: function(vnode) {
		// TODO: Focus on Motiu
		console.debug(vnode.children);
	},
	oninit: function(vnode) {
		vnode.state.busy = vnode.attrs.busy;
	},
	view: function(vnode) {
		var busy = vnode.attrs.busy;
		return m('.busyentryeditor', [
			m(Textfield, {
				label: 'Motiu',
				floatingLabel: true,
				autofocus: 1,
				help: 'Explica el motiu, com a referència',
				required: true,
				value: busy.reason,
				onChange: function(state) {
					busy.reason=state.value;
				},
			}),
			m('.pe-textfield.pe-textfield--dirty.pe-textfield--floating-label', [
				m('.pe-textfield__input-area', [
					m('label[for=optional].pe-textfield__label',
						"Opcional?"),
					m(RadioGroup, {
						name: 'optional',
						id: 'optional',
						onChange: function(state) {
							busy.optional = state.value=='y';
						},
						className: 'layout.pe-textfield__input',
						all: {
							className: 'flex',
						},
						buttons: [
							{
								label: 'Sí',
								value: 'y',
								checked: busy.optional,
							},
							{
								label: 'No',
								value: 'n',
								checked: !busy.optional,
							},
						],
					}),
					m('.pe-textfield__help',
						"Es pot descartar si estem apurats?"),
				])
			]),
			busy.weekday !== undefined ?
				m(Select, {
					label: 'Dia de la setmana',
					value: busy.weekday,
					options: {
						'': 'Tots els dies',
						dl: 'Dilluns',
						dm: 'Dimarts',
						dx: 'Dimecres',
						dj: 'Dijous',
						dv: 'Divendres',
					},
					onChange: function(ev) {
						busy.weekday = ev.target.value;
					},
				}):[],
			/*
			busy.weekday === undefined ?
				m(Textfield, {
					label: 'Data',
					pattern: '20[0-9]{2}-[01][0-9]-[0-3][0-9]$',
					error: 'Data en format ISO YYYY-MM-DD',
					floatingLabel: true,
					help: 'Especifica la data concreta de la indisponibilitat',
					required: true,
					validate: function(value) {
						console.debug("Validating: ", value);
						if (!isNaN(Date.parse(value))) {return {valid: true};}
						return {
							valid: false,
							error: 'Data en format ISO YYYY-MM-DD',
						};
					},
					value: busy.date,
					onChange: function(state) {
						console.debug("Changing date:",busy.date, "->", state.value);
						busy.date=state.value;
					},
				}):[],
			*/
			busy.weekday === undefined ?
				m(DatePicker, {
					date: Date.parse(busy.date),
					onchange: function(newDate) {
						busy.date=newDate.toISOString().substr(0,10)+'';
						console.debug("date:",busy.date);
					},
					locale: 'ca',
					weekstart: 1,
				}):[],
			m('p.label', "Marca les hores que no estaràs disponible:"),
			Array.from(busy.turns).map(function(active, i) {
				var hours = Tomatic.grid().hours;
				return m('', m(Checkbox, {
					label: hours[i]+' - '+hours[i+1],
					checked: active==='1',
					onChange: function(state) {
						console.debug("onchange:",state);
						console.debug('Before:',busy.turns);
						busy.turns = (
							busy.turns.substr(0,i)+
							((busy.turns[i]==='1')?'0':'1')+
							busy.turns.substr(i+1)
						);
						console.debug('After:',busy.turns);
					},
				}));
			}),
		]);
	},
};

var editAvailability = function(receivedData, updateCallback) {
	var busy = Object.assign({}, receivedData);
	Dialog.show(function () { return {
		id: 'BusyEditor',
		title: 'Edita indisponibilitat',
		backdrop: true,
		body: m(BusyEntryEditor, {
			busy: busy,
		}),
		footerButtons: [
			m(Button, {
				label: "Accepta",
				events: {
					onclick: function() {
						updateCallback(busy);
						Dialog.hide({id:'BusyEditor'});
					},
				},
				disabled: !busy.reason,
			}),
			m(Button, {
				label: "Cancel·la",
				events: {
					onclick: function() {
						Dialog.hide({id:'BusyEditor'});
					},
				},
			}),
		],
	};},{id: 'BusyEditor'});
};


var editAvailabilities = function(name) {
	Tomatic.retrieveBusyData(name, function(data) {
		Dialog.show(function () { return {
			id: 'BusyListEditor',
			title: 'Edita indisponibilitats '+Tomatic.formatName(name),
			backdrop: true,
			body: [
				m('.busylist', [
					m(BusyList, {
						title: 'Setmanals',
						entries: data.weekly,
						isOneShot: false,
						onChange: function() {
							console.log("Updating data:\n",data);
							Tomatic.sendBusyData(name, data);
						},
					}),
					m(BusyList, {
						title: 'Puntuals',
						entries: data.oneshot,
						isOneShot: true,
						onChange: function() {
							console.log("Updating data:\n",data);
							Tomatic.sendBusyData(name, data);
						},
					}),
				]),
			],
			footerButtons: [
				m(Button, {
					label: "Tanca",
					events: {
						onclick: function() {
							Dialog.hide({id:'BusyListEditor'});
						},
					},
				}),
			],
		};}, {id: 'BusyListEditor'});
		//m.redraw();
	});
};


return editAvailabilities;
}();

