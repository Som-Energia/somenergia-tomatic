var m = require('mithril')
var QueueMonitor = require('./queuemonitor')
var Doc = require('./doc').default

const PbxPage = {
	view: function () {
		return m('', [
			Doc(
				m(
					'',
					'Visualitza les línies que estan actualment rebent trucades. ' +
						"Feu click al damunt per pausar-les o al signe '+' per afegir-ne"
				)
			),
			m('h2[style=text-align:center]', 'Linies en cua'),
			m(QueueMonitor),
		])
	},
}

export default PbxPage

// vim: noet ts=4 sw=4