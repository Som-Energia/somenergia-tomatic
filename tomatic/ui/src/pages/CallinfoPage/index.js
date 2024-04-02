import React from 'react'
import Stack from '@mui/material/Stack'
import CircularProgress from '@mui/material/CircularProgress'
import CallInfo from '../../contexts/callinfo'
import AttendedCalls from './AttendedCalls'
import CustomerSearch from './CustomerSearch'
import PartnerInfo from './PartnerInfo'
import ContractInfo from './ContractInfo'
import DetailsInfo from './DetailsInfo'
import './style.styl'

function Spinner() {
  return <CircularProgress />
}

export default function CallinfoPage() {
  const results = CallInfo.results.use()
  return (
    <div className="callinfo">
      <Stack className="all-info-call" direction="row">
        <AttendedCalls />
        <Stack direction="row" flex={1}>
          <Stack direction="column" flex={1}>
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
                  <Stack direction="column" flex={1}>
                    <PartnerInfo />
                    <ContractInfo />
                  </Stack>
                  <DetailsInfo data={results} />
                </div>
              )}
            </div>
          </Stack>
        </Stack>
      </Stack>
    </div>
  )
}
