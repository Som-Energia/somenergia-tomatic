import React, {useState} from 'react'
import Tomatic from '../services/tomatic';
import Auth from '../services/auth';

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';

import EditDialog from './EditDialog';

function TimeTable() {
    const grid = Tomatic.grid()

    const [gridData, setGridData] = useState(grid)
    const [dialogIsOpen, setDialogIsOpen] = useState(false)
    const [cellData, setCellData] = useState({})

    const openDialog = () => setDialogIsOpen(true)
  
    const closeDialog = () => setDialogIsOpen(false)

    const handleClick = (day, houri, turni) => {
    	setCellData({day:day, hour:houri, turn:turni});
        openDialog()
	}

    function cell (day, houri, turni) {
        var name = Tomatic.cell(day, houri, turni)
        return (
            <Tooltip title={Tomatic.formatExtension(name)} placement="top-end">
                <TableCell className={name} onClick={() => handleClick(day, houri, turni)}>{Tomatic.formatName(name)}
                </TableCell>
            </Tooltip>
        )
    }    

    const handleChange = (name, data) => {
        var myname = Auth.username();
        Tomatic.editCell(data.day, data.hour, data.turn, name, myname)
        closeDialog();
    }


    return (
        <>
        {dialogIsOpen 
        ? <EditDialog open={dialogIsOpen} data={cellData} handleChange={handleChange} onClose={closeDialog}></EditDialog>
        : null }
        <TableContainer className='.graella' component={Paper}>
        {gridData?.days.map((day) =>
        <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
            <TableHead>
            <TableRow>
                <TableCell>{Tomatic.weekday(day)}</TableCell>
                {gridData?.turns.map((turn) => 
                    <TableCell align="left">{turn}</TableCell>
                )}
            </TableRow>
            </TableHead>
            <TableBody>
            {gridData?.hours.slice(0, -1).map((hour, houri) => (
                <TableRow
                key={hour}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                <TableCell component="th" scope="row">
                    {gridData?.hours[houri] + '-' + gridData?.hours[houri + 1]}
                </TableCell>
                {gridData.turns.map((turn, turni) => cell(day, houri, turni))}
                </TableRow>
            ))}
            </TableBody>
        </Table>
        )}
        </TableContainer>
        </>
    )
}

export default TimeTable