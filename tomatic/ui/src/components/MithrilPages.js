// MithrilPages
//
// Provides old Mithril application pages as React Components
// to be included in the React app as is.

import * as React from 'react'
import MithrilWrapper from '../containers/MithrilWrapper'
import MithrilStyler from '../containers/MithrilStyler'
import TimeTablePage from '../mithril/components/timetablepage'
import CallinfoPage from '../mithril/components/callinfopage'
import PbxPage from '../mithril/components/pbxpage'

function MithrilCallinfoPage() {
  return <MithrilWrapper component={MithrilStyler(CallinfoPage)} />
}

function MithrilTimeTablePage() {
  return <MithrilWrapper component={MithrilStyler(TimeTablePage)} />
}

function MithrilQueueMonitor() {
  return <MithrilWrapper component={MithrilStyler(PbxPage)} />
}

export { MithrilCallinfoPage, MithrilQueueMonitor, MithrilTimeTablePage }
