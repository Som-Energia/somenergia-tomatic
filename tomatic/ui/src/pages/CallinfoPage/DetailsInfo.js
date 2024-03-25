import React from 'react'
import Box from '@mui/material/Box'
import TabbedCard from './TabbedCard'
import AtrCases from './AtrCases'
import Invoices from './Invoices'
import Meterings from './Meterings'
import CallInfo from '../../contexts/callinfo'
import { useSubscriptable } from '../../services/subscriptable'

export default function DetailsInfo() {
  const [activeView, setActiveView] = React.useState(0)
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
          {activeView === 1 && <Invoices />}
          {activeView === 2 && <Meterings />}
        </Box>
      </TabbedCard>
    </Box>
  )
}
