// MithrilPages
//
// Provides old Mithril application pages as React Components
// to be included in the React app as is.

import * as React from 'react'
import MithrilWrapper from '../containers/MithrilWrapper'
import MithrilStyler from '../containers/MithrilStyler'
import PersonsPage from '../mithril/components/personspage'

function MithrilPersonsPage() {
  return <MithrilWrapper component={MithrilStyler(PersonsPage)} />
}

export { MithrilPersonsPage }
