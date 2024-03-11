import React from 'react'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import m from '../../services/hyperscript'
import TabbedCard from './TabbedCard'
import AtrCases from './AtrCases'
import Meterings from './Meterings'
import CallInfo from '../../mithril/components/callinfo'
import { useSubscriptable } from '../../services/subscriptable'

export default function DetailsInfo() {
  const [activeView, setActiveView] = React.useState(0)
  const views = ['atr', 'invoices', 'readings']
  const contract = useSubscriptable(CallInfo.selectedContract)
  useSubscriptable(CallInfo.results)

  if (contract === null) return null

  return (
    <Box className={'contract-details flex'}>
      <TabbedCard
        currentTab={activeView}
        onTabChanged={(value) => {
          setActiveView(value)
          if (value) {
            CallInfo.notifyUsage('callinfoChangeDetails')
          }
        }}
        labels={['ATR', 'Factures', 'Lectures']}
      >
        <Box className="contract-info-box">
          {activeView === 0 && <AtrCases />}
          {/* activeView === 1 && <Invoices invoices={contract.invoices} /> */}
          { activeView === 2 && <Meterings /> }
        </Box>
      </TabbedCard>
    </Box>
  )
}
