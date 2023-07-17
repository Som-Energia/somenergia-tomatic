import React, {useState, useEffect} from 'react'
import Tomatic from '../services/tomatic'
import TimeTable from './TimeTable'
import Doc from './Doc'
import Typography from '@mui/material/Typography';

var onForcedTurnsUpdated = null
Tomatic.onForcedTurnsUpdated.push(()=>
    onForcedTurnsUpdated && onForcedTurnsUpdated()
)

function ForcedTurns() {
    const [grid, setGrid]= useState()

    onForcedTurnsUpdated = () => {
        setGrid(Tomatic.forcedTurns())
    }

    useEffect(onForcedTurnsUpdated, [Tomatic.forcedTurns()])

    const setCell = (day, houri, turni, name) => {
        Tomatic.editForcedTurn(day, houri, turni, name)
    }
    const getCell = (day, houri, turni) => {
        return Tomatic.forcedTurnCell(day, houri, turni)
    }
    return (
        <>
        <Doc
            message="Visualitza la graella de torns fixats. Feu click al damunt d'una cel·la per bescanviar el turn."
        ></Doc>
        <Typography gutterBottom variant="h2" align="center" component="div">
            Torns fixats
        </Typography>
        <TimeTable
            grid={grid}
            setCell={setCell}
            getCell={getCell}
        ></TimeTable>
        </>
    )
}

export default ForcedTurns