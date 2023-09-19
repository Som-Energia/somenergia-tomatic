import m from 'mithril'
import QueueMonitor from './queuemonitor'
import Doc from './doc'

const PbxPage = {
  view: function () {
    return m('', [
      Doc(
        m(
          '',
          'Visualitza les línies que estan actualment rebent trucades. ' +
            "Feu click al damunt per pausar-les o al signe '+' per afegir-ne",
        ),
      ),
      m('h2[style=text-align:center]', 'Linies en cua'),
      m(QueueMonitor),
    ])
  },
}

export default PbxPage

// vim: et ts=2 sw=2
