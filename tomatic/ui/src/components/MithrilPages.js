// MithrilPages
//
// Provides old Mithril application pages as React Components
// to be included in the React app as is.

import * as React from 'react'
import MithrilWrapper from '../containers/MithrilWrapper'
import MithrilStyler from '../containers/MithrilStyler'
import CallinfoPage from '../mithril/components/callinfopage'
import PbxPage from '../mithril/components/pbxpage'
import PersonsPage from '../mithril/components/personspage'

function MithrilCallinfoPage() {
  return <MithrilWrapper component={MithrilStyler(CallinfoPage)} />
}

function MithrilQueueMonitor() {
  return <MithrilWrapper component={MithrilStyler(PbxPage)} />
}

function MithrilPersonsPage() {
  return <MithrilWrapper component={MithrilStyler(PersonsPage)} />
}

export {
  MithrilCallinfoPage,
  MithrilQueueMonitor,
  MithrilPersonsPage,
}
