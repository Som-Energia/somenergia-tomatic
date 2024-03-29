import React from 'react'
import Tomatic from '../services/tomatic'
import TimeTable from './TimeTable'
import Box from '@mui/material/Box'
import WeekPicker from './WeekPicker'

function TimeTablePage() {
  const grid = Tomatic.grid.use()

  const setCell = (day, houri, turni, name) => {
    Tomatic.editCell(day, houri, turni, name)
  }
  const getCell = (day, houri, turni) => {
    return Tomatic.cell(day, houri, turni)
  }
  return (
    <>
      <Box
        sx={{
          p: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          '& > *': {
            m: 1,
          },
        }}
      >
        <WeekPicker />
        <TimeTable
          grid={grid}
          setCell={setCell}
          getCell={getCell}
          showPenalties={true}
          showOverloads={true}
        ></TimeTable>
      </Box>
    </>
  )
}

export default TimeTablePage
