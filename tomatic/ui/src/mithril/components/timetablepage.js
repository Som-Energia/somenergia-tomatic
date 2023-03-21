// TimeTablePage
// Page to browse timetables for each week
module.exports = (function () {
	var m = require('mithril')
	var Dialog = require('polythene-mithril-dialog').Dialog
	var Button = require('polythene-mithril-button').Button
	var Ripple = require('polythene-mithril-ripple').Ripple
	var Tomatic = require('./tomatic')
	var WeekPicker = require('./weekpicker')
	var Uploader = require('./uploader')
	var PersonPicker = require('./personpicker')
	var Auth = require('./auth')

	var TimeTable = function (grid) {
		var editCell = function (day, houri, turni) {
			var setPerson = function (name) {
				var myname = Auth.username()
				Tomatic.editCell(day, houri, turni, name, myname)
				Dialog.hide({ id: 'GridCellEditor' })
			}
			var oldPerson = Tomatic.cell(day, houri, turni)
			Dialog.show(
				{
					id: 'GridCellEditor',
					className: 'grid-cell-editor',
					title: 'Edita posició de la graella',
					backdrop: true,
					body: [
						Tomatic.weekday(day) +
							' a les ' +
							Tomatic.grid().hours[houri] +
							', línia ' +
							(turni + 1) +
							', la feia ',
						m(
							'span.extension.' + oldPerson,
							Tomatic.formatName(oldPerson)
						),
						' qui ho ha de fer?',
						m(PersonPicker, {
							id: 'GridCellEditor',
							onpick: setPerson,
							nobodyPickable: true,
						}),
					],
					footerButtons: [
						m(Button, {
							label: 'Cancel·la',
							events: {
								onclick: function () {
									Dialog.hide({ id: 'GridCellEditor' })
								},
							},
						}),
					],
				},
				{ id: 'GridCellEditor' }
			)
		}
		var cell = function (day, houri, turni) {
			var name = Tomatic.cell(day, houri, turni)
			return m(
				'td',
				{
					className: name || 'ningu',
					onclick: function (ev) {
						ev.preventDefault()
						if (Auth.username() === '') {
							return
						}
						editCell(day, houri, turni)
					},
				},
				[
					Tomatic.formatName(name),
					Tomatic.persons().extensions[name]
						? m('.tooltip', Tomatic.persons().extensions[name])
						: [],
					m(Ripple),
				]
			)
		}
		if (!grid.turns) {
			return []
		}
		return [
			(grid.days || []).map(function (day, dayi) {
				return m(
					'.graella',
					m('table', [
						m('tr', [
							m('td'),
							m(
								'th',
								{ colspan: grid.turns.length },
								Tomatic.weekday(day)
							),
						]),
						m('td'),
						grid.turns.map(function (turn) {
							return m('th', turn)
						}),
						grid.hours.slice(0, -1).map(function (hour, houri) {
							return m('tr', [
								dayi !== 0 && false
									? m('th.separator', m.trust('&nbsp;'))
									: m(
											'th.separator',
											grid.hours[houri] +
												'-' +
												grid.hours[houri + 1]
									  ),
								grid.turns.map(function (turn, turni) {
									return cell(day, houri, turni)
								}),
							])
						}),
					])
				)
			}),
		]
	}

	var Extensions = function (extensions) {
		return [
			m(
				'.extensions',
				Object.keys(extensions || {})
					.sort()
					.map(function (name) {
						return m('.extension', { className: name }, [
							Tomatic.formatName(name),
							m('br'),
							extensions[name],
						])
					})
			),
		]
	}
	var Changelog = function (grid) {
		return m('.graella', [
			m('h5', 'Darrers canvis'),
			m('ul.changelog', [
				grid.log ? [] : m('li', 'Cap canvi registrat'),
				(grid.log || [])
					.slice(0, -1)
					.reverse()
					.map(function (change) {
						return m('li', change)
					}),
				(grid.log || []).length > 5 ? m('li', m.trust('&hellip;')) : [],
			]),
		])
	}
	var Penalties = function (grid) {
		return m('.graella', [
			m('h5', 'Penalitzacions (', grid.cost || 0, ' punts)'),
			m('ul.penalties', [
				grid.penalties
					? []
					: m('li', 'La graella no te penalitzacions'),
				(grid.penalties || []).map(function (penalty) {
					return m('li', penalty[0], ': ', penalty[1])
				}),
			]),
		])
	}

	var Overloads = function (grid) {
		return m('.graella', [
			m('h5', "Sobrecarrega respecte l'ideal"),
			m('ul.overloads', [
				grid.overload
					? []
					: m('li', 'La graella no te sobrecarregues apuntades'),
				Object.keys(grid.overload || {}).map(function (person) {
					return m('li', person, ': ', grid.overload[person])
				}),
			]),
		])
	}

	var TimeTablePage = {
		view: function () {
			var grid = Tomatic.grid()
			return m('', [
				m('.layout.vertical', [
					m(WeekPicker),
					m('.layout.end-justified', [
						m(Uploader, {
							name: 'yaml',
							label: 'Puja Nova Graella',
							url: 'api/graella',
							onupload: function (result) {
								Tomatic.init()
							},
							onerror: function (error) {
								console.log('Upload error:', error)
								Tomatic.error('Upload error: ' + error.error)
							},
						}),
					]),
				]),
				m('.layout.center-center.wrap', TimeTable(grid)),
				Extensions(grid.otherextensions),
				m('.layout.around-justified.wrap', [
					Changelog(grid),
					Penalties(grid),
					Overloads(grid),
				]),
			])
		},
	}

	return TimeTablePage
})()
// vim: noet sw=4 ts=4
