var CallInfoPage = require('../mithril/components/callinfopage')
var Tomatic = require('../services/tomatic')
const { redirect, useNavigate } = require('react-router-dom')

const scriptLauncherBase = 'http://tomatic.somenergia.lan:5000'
const menuOptions = function () {
	return [
		{
			icon: '🕜',
			title: 'Planificador de Graelles',
			action: function () {
				window.location.href = '/api/planner/'
			},
		},
		{
			icon: '📊',
			title: 'Estadístiques de trucades',
			action: function () {
				window.location.href =
					scriptLauncherBase + '/runner/statshistory'
			},
		},
		{
			icon: '📢',
			title: 'En Tomàtic diu...',
			action: function () {
				window.location.href = scriptLauncherBase + '/runner/says'
			},
		},
		{
			icon: '🔄',
			title: 'Restableix el torn a la cua',
			action: function () {
				window.location.href =
					scriptLauncherBase + '/runner/reloadqueue'
			},
		},
		{
			icon: '🏷️',
			title: 'Anotacions: Actualitza categories',
			action: function () {
				CallInfoPage.settingsDialog()
			},
		},
		{
			icon: '🚀',
			title: 'Altres scripts de Centraleta',
			action: function () {
				window.location.href = scriptLauncherBase
			},
		},
		{
			icon: '😎',
			title: 'Kumato mode',
			action: function () {
				Tomatic.toggleKumato()
			},
		},
		{
			icon: '🦸‍♀️',
			title: 'Administració',
			route: '/Administration',
		},
		{
			icon: '🛟',
			navigation: true,
			title: "Guies d'usuaria i videos",
			action: function () {
				const url =
					'https://github.com/Som-Energia/somenergia-tomatic/blob/master/doc/userguide.md'
				window.open(url, '_blank')
			},
		},
	]
}
export default menuOptions

// vim: noet ts=4 sw=4
