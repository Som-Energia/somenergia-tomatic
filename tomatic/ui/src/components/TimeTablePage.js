import React, {useState, useEffect} from 'react'
import Tomatic from '../services/tomatic'
import TimeTable from './TimeTable'
import Box from '@mui/material/Box'
import WeekPicker from './WeekPicker'

var onGridUpdated = null
Tomatic.onGridUpdated.push(()=>
onGridUpdated && onGridUpdated()
)

function TimeTablePage() {
    const [grid, setGrid]= useState()

    onGridUpdated = () => {
        setGrid(Tomatic.grid())
    }

    useEffect(onGridUpdated, [Tomatic.grid()])

    const setCell = (day, houri, turni, name) => {
        Tomatic.editCell(day, houri, turni, name)
    }
    const getCell = (day, houri, turni) => {
        return Tomatic.cell(day, houri, turni)
    }
    return (
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
        <WeekPicker></WeekPicker>
        <TimeTable
            grid={grid}
            setCell={setCell}
            getCell={getCell}
            showPenalties={true}
            showOverloads={true}
        ></TimeTable>
        </Box>
    )
}

export default TimeTablePage