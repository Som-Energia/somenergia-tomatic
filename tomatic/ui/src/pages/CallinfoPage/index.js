import React from 'react'
import CallInfo from '../../mithril/components/callinfo'
import AttendedCalls from './AttendedCalls'
import CustomerSearch from './CustomerSearch'
import {useSubscriptable} from '../../services/subscriptable'

function Spinner() {
  return <>Spinner</>
}
function PartnerInfo() {
  return <>Partner Info</>
}
function ContractInfo() {
  return <>Contract Info</>
}
function DetailsInfo() {
  return <>Details Info</>
}

export default function CallinfoPage() {
  const results = useSubscriptable(CallInfo.results)
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
                    <PartnerInfo data={results} />
                    <ContractInfo data={results} />
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
