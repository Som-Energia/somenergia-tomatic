import React from 'react'
import CircularProgress from '@mui/material/CircularProgress'
import Paper from '@mui/material/Paper'
import CallInfo from '../../mithril/components/callinfo'
import AttendedCalls from './AttendedCalls'
import CustomerSearch from './CustomerSearch'
import PartnerInfo from './PartnerInfo'
import ContractInfo from './ContractInfo'
import { useSubscriptable } from '../../services/subscriptable'

function Spinner() {
  return <CircularProgress />
}

function DetailsInfo() {
  return <Paper>Details Info</Paper>
}

export default function CallinfoPage() {
  const results = useSubscriptable(CallInfo.results)
  const [currentPartner, setCurrentPartner] = React.useState(0)
  const [currentContract, setCurrentContract] = React.useState(0)
  console.log("CallinfoPage", {currentContract})
  return (
    <div className="callinfo">
      <div className="all-info-call layout horizontal">
        <AttendedCalls />

        <div className="layout horizontal flex">
          <div className="layout vertical flex">
            <CustomerSearch />
            <div className="plane-info">
              {CallInfo.searchStatus() === 'ZERORESULTS' ? (
                <div className="searching">
                  {"No s'ha trobat cap resultat."}
                </div>
              ) : CallInfo.searchStatus() === 'SEARCHING' ? (
                <div className="searching">
                  <Spinner show />
                </div>
              ) : CallInfo.searchStatus() === 'ERROR' ? (
                <div className="searching">
                  {"S'ha produït un error en la cerca."}
                </div>
              ) : CallInfo.searchStatus() === 'TOOMANYRESULTS' ? (
                <div className="searching">
                  {'Cerca poc específica, retorna masses resultats.'}
                </div>
              ) : (
                <div className="plane-info">
                  <div className="layout vertical flex">
                    <PartnerInfo
                      data={results}
                      {...{ currentPartner, setCurrentPartner }}
                    />
                    <ContractInfo
                      data={results}
                      {...{
                        currentPartner,
                        setCurrentPartner,
                        currentContract,
                        setCurrentContract,
                      }}
                    />
                  </div>
                  <DetailsInfo data={results} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
