import * as React from 'react'
import m from 'mithril'
import { Dialog } from 'polythene-mithril-dialog'
import * as css from 'polythene-css'
import MithrilWrapper from '../containers/MithrilWrapper'
import TimeTablePage from '../mithril/components/timetablepage'
import CallinfoPage from '../mithril/components/callinfopage'
import PbxPage from '../mithril/components/pbxpage'
import PersonStyles from '../mithril/components/personstyles'
import Tomatic from '../services/tomatic'
import customStyle from '../mithril/style.styl'

css.addLayoutStyles()
css.addTypography()
console.log('customStyle', customStyle)
const Wrapper = (mithrilComponent) => {
  return {
    view: (vnode) => {
      return m(
        '#tomatic.main' + '.variant-' + Tomatic.variant,
        m(
          '',
          PersonStyles(),
          m(Tomatic.isKumatoMode() ? 'pe-dark-tone' : '', [
            m(mithrilComponent),
            m(Dialog),
          ])
        )
      )
    },
  }
}

function MithrilCallinfoPage() {
  return <MithrilWrapper component={Wrapper(CallinfoPage)} />
}

function MithrilTimeTablePage() {
  return <MithrilWrapper component={Wrapper(TimeTablePage)} />
}

function MithrilQueueMonitor() {
  return <MithrilWrapper component={Wrapper(PbxPage)} />
}

export { MithrilCallinfoPage, MithrilQueueMonitor, MithrilTimeTablePage }
