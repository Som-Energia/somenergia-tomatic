import React from 'react'
import Tomatic from '../services/tomatic'
import TimeTable from './TimeTable'
import Doc from './Doc'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import { useSubscriptable } from '../services/subscriptable'

function ForcedTurns() {
  const grid = useSubscriptable(Tomatic.forcedTurns)

  const setCell = (day, houri, turni, name) => {
    Tomatic.editForcedTurn(day, houri, turni, name)
  }
  const getCell = (day, houri, turni) => {
    return Tomatic.forcedTurnCell(day, houri, turni)
  }
  const addColumn = () => {
    Tomatic.forcedTurnsAddColumn()
  }
  const removeColumn = () => {
    Tomatic.forcedTurnsRemoveColumn()
  }

  return (
    <>
      <Doc message="Els torns fixats es tenen en compte per generar la grella cada setmana si n'hi ha disponibilitat. Feu click al damunt d'una cel·la per bescanviar el turn."></Doc>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          '& > *': {
            m: 1,
          },
        }}
      >
        <Typography gutterBottom variant="h2" component="div">
          Torns fixats
        </Typography>
        <TimeTable
          grid={grid}
          setCell={setCell}
          getCell={getCell}
          addColumn={addColumn}
          removeColumn={removeColumn}
        ></TimeTable>
      </Box>
    </>
  )
}

export default ForcedTurns
