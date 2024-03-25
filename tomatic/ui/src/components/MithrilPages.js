// MithrilPages
//
// Provides old Mithril application pages as React Components
// to be included in the React app as is.

import * as React from 'react'
import MithrilWrapper from '../containers/MithrilWrapper'
import MithrilStyler from '../containers/MithrilStyler'
import PbxPage from '../mithril/components/pbxpage'
import PersonsPage from '../mithril/components/personspage'

function MithrilQueueMonitor() {
  return <MithrilWrapper component={MithrilStyler(PbxPage)} />
}

function MithrilPersonsPage() {
  return <MithrilWrapper component={MithrilStyler(PersonsPage)} />
}

export { MithrilQueueMonitor, MithrilPersonsPage }
