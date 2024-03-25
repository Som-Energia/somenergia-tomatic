import React from 'react'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import CallInfo from '../../contexts/callinfo'
import { useSubscriptable } from '../../services/subscriptable'

export default function AtrCases() {
  const cases = useSubscriptable(CallInfo.contractDetails).atr_cases
  if (cases === null) {
    return (
      <Box className="atr-cases">
        <Box className="loading  layout vertical center">
          {'Carregant casos ATR...'}
          <CircularProgress />
        </Box>
      </Box>
    )
  }
  if (cases.length === 0) {
    return (
      <Box className="atr-cases">
        <Box className="loading  layout vertical center">
          {'No hi ha casos ATR disponibles.'}
        </Box>
      </Box>
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
