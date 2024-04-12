import React from 'react'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import CallInfo from '../../contexts/callinfo'
import Solo from '../../components/Solo'
import { useSubscriptable } from '../../services/subscriptable'

export default function AtrCases() {
  const isLoading = CallInfo.loadingDetails.use()
  const contract = useSubscriptable(CallInfo.selectedContract)
  const cases = contract?.atr_cases ?? null
  if (isLoading) {
    return (
      <Solo className="atr-cases">
        {'Carregant casos ATR...'}
        <CircularProgress />
      </Solo>
    )
  }
  if (cases.length === 0) {
    return (
      <Solo className="atr-cases">{'No hi ha casos ATR disponibles.'}</Solo>
    )
  }
  return (
    <Box className="atr-cases">
      <table>
        <thead>
          <tr>
            <th>{'Data'}</th>
            <th>{'Procés'}</th>
            <th>{'Pas'}</th>
            <th>{'Estat'}</th>
            <th>{'Descripció'}</th>
          </tr>
        </thead>
        <tbody>
          {cases.map(function (atr_case, i) {
            return (
              <tr key={i}>
                <td>
                  {
                    // Date not time
                    atr_case.date.slice(0, 10)
                  }
                </td>
                <td>{atr_case.proces}</td>
                <td>{atr_case.step}</td>
                <td>
                  <span
                    className={atr_case.state !== 'done' ? '.alert-case' : ''}
                  >
                    {atr_case.state}
                  </span>
                </td>
                <td>
                  <span title={atr_case.additional_info}>
                    {atr_case.additional_info}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </Box>
  )
}
