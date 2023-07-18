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
            message="Els torns fixats es tenen en compte per generar la grella cada setmana si n'hi ha disponibilitat. Feu click al damunt d'una cel·la per bescanviar el turn."
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