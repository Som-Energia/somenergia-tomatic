import React from 'react'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import CallInfo from '../../mithril/components/callinfo'
import { useSubscriptable } from '../../services/subscriptable'

export default function Meterings() {
  const readings = useSubscriptable(
    CallInfo.contractDetails,
  ).lectures_comptadors
  if (readings === null) {
    return (
      <Box className="meter-readings">
        <Box className="loading  layout vertical center">
          {'Carregant lectures...'}
          <CircularProgress />
        </Box>
      </Box>
    )
  }
  if (readings.length === 0) {
    return (
      <Box className="meter-readings">
        <Box className="loading  layout vertical center">
          {'No hi ha lectures disponibles.'}
        </Box>
      </Box>
    )
  }
  return (
    <Box className="meter-readings">
      <table>
        <thead>
          <tr>
            <th>{'Comptador'}</th>
            <th>{'Data'}</th>
            <th>{'Lectura'}</th>
            <th>{'Origen'}</th>
            <th>{'Període'}</th>
          </tr>
        </thead>
        <tbody>
          {readings.map(function (reading, i) {
            return (
              <tr key={i}>
                <td>{reading.comptador}</td>
                <td>{reading.data}</td>
                <td>{reading.lectura}</td>
                <td>{reading.origen}</td>
                <td>{reading.periode}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </Box>
  )
}
