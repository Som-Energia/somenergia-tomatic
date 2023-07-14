import React, {useState} from 'react'
import Tomatic from '../services/tomatic'
import TimeTable from './TimeTable'

var onForcedTurnsUpdated = null
Tomatic.onForcedTurnsUpdated.push(()=>
    onForcedTurnsUpdated && onForcedTurnsUpdated()
)

function ForcedTurns() {
    const [grid, setGrid]= useState()

    onForcedTurnsUpdated = () => {
        setGrid(Tomatic.forcedTurns())
    }
    const setCell = (day, houri, turni, name) => {
        Tomatic.editForcedTurn(day, houri, turni, name)
    }
    const getCell = (day, houri, turni) => {
        return Tomatic.forcedTurnCell(day, houri, turni)
    }
    return (
        <TimeTable
            grid={grid}
            setCell={setCell}
            getCell={getCell}
        ></TimeTable>
    )
}

export default ForcedTurns