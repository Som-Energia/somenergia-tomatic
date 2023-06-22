var CallInfoPage = require('../mithril/components/callinfopage')
var Tomatic = require('../services/tomatic')
const { redirect, useNavigate } = require('react-router-dom')

const scriptLauncherBase = window.location.protocol + '//' + window.location.hostname + ':5000'

const menuOptions = function () {
	return [
		{
			icon: '🕜',
			title: 'Planificador de Graelles',
			action: function () {
				const url = '/api/planner/'
				window.open(url, '_blank')
			},
		},
		{
			icon: '📊',
			title: 'Estadístiques de trucades',
			action: function () {
				const url = scriptLauncherBase + '/runner/statshistory'
				window.open(url, '_blank')
			},
		},
		{
			icon: '📢',
			title: 'En Tomàtic diu...',
			action: function () {
				const url = scriptLauncherBase + '/runner/says'
				window.open(url, '_blank')
			},
		},
		{
			icon: '🔄',
			title: 'Restableix el torn a la cua',
			action: function () {
				const url = scriptLauncherBase + '/runner/reloadqueue'
				window.open(url, '_blank')
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
				const url = scriptLauncherBase
				window.open(url, '_blank')
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
