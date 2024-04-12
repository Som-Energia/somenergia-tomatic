import React from 'react'
import Tomatic from '../services/tomatic'
import TimeTable from './TimeTable'
import Stack from '@mui/material/Stack'
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
      <Stack
        p="0"
        display="flex"
        flexDirection="column"
        alignItems="center"
        sx={{
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
      </Stack>
    </>
  )
}

export default TimeTablePage
