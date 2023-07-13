import React, {useState} from 'react'
import Tomatic from '../services/tomatic';
import Auth from '../services/auth';

import PersonStyles from './PersonStyles'
import customStyle from '../mithril/style.styl'

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
            <td className={name} onClick={() => handleClick(day, houri, turni)}>
                {Tomatic.formatName(name)}
                <div className="tooltip" >
                    {Tomatic.formatExtension(name)}
                </div>
            </td>
        )
    }    

    const handleChange = (name, data) => {
        var myname = Auth.username();
        Tomatic.editCell(data.day, data.hour, data.turn, name, myname)
        closeDialog();
    }

    return (
        <>
        <PersonStyles />
        {dialogIsOpen 
        ? <EditDialog open={dialogIsOpen} data={cellData} handleChange={handleChange} onClose={closeDialog}></EditDialog>
        : null }
        <div className='layout center-center wrap'>
        <div className='graella'>
            {gridData?.days.map((day) =>
            <table>
                <thead>
                    <tr>
                        <th>{Tomatic.weekday(day)}</th>
                        {gridData?.turns.map((turn) =>
                            <td>{turn}</td>
                        )}
                    </tr>
                </thead>
                <tbody>
                    {gridData?.hours.slice(0, -1).map((hour, houri) => (
                        <tr key={hour}>
                        <th className='separator'>
                            {gridData?.hours[houri] + '-' + gridData?.hours[houri + 1]}
                        </th>
                        {gridData.turns.map((turn, turni) => cell(day, houri, turni))}
                        </tr>
                    ))}
                </tbody>
            </table>
            )}
        </div>
        </div>
        </>
    )
}

export default TimeTable