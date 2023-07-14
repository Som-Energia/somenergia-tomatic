import React, {useState} from 'react'
import Tomatic from '../services/tomatic';

import PersonStyles from './PersonStyles'
import customStyle from '../mithril/style.styl'

import EditDialog from './EditDialog';

function TimeTable(props) {
    const {grid, setCell, getCell} = props

    const [dialogIsOpen, setDialogIsOpen] = useState(false)
    const [cellData, setCellData] = useState({})

    const openDialog = () => setDialogIsOpen(true)
  
    const closeDialog = () => setDialogIsOpen(false)

    const handleClick = (day, houri, turni) => {
    	setCellData({day:day, hour:houri, turn:turni});
        openDialog()
	}

    function cell (day, houri, turni) {
        var name = getCell(day, houri, turni)
        return (
            <td className={name} onClick={() => handleClick(day, houri, turni)}>
                {Tomatic.formatName(name)}
                <div className="tooltip" >
                    {Tomatic.formatExtension(name)}
                </div>
            </td>
        )
    }    

    function Changelog(grid) {
        return (
            <div className='graella'>
                <h5>Darrers canvis</h5>
                <ul className='changelog'>
                    {grid.log? [] : <li>'Cap canvi registrat'</li>}
                    {grid.log.slice(0, -1).reverse().map((change) => (
                        <li>{change}</li>
                    ))
                    }
                </ul>
            </div>
        )
	}

    const handleChange = (name, data) => {
        setCell(data.day, data.hour, data.turn, name)
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
            {grid?.days.map((day) =>
            <table>
                <thead>
                    <tr>
                        <th>{Tomatic.weekday(day)}</th>
                        {grid?.turns.map((turn) =>
                            <td>{turn}</td>
                        )}
                    </tr>
                </thead>
                <tbody>
                    {grid?.hours.slice(0, -1).map((hour, houri) => (
                        <tr key={hour}>
                        <th className='separator'>
                            {grid?.hours[houri] + '-' + grid?.hours[houri + 1]}
                        </th>
                        {grid.turns.map((turn, turni) => cell(day, houri, turni))}
                        </tr>
                    ))}
                </tbody>
            </table>
            )}
        </div>
        </div>
        <div className='layout.around-justified.wrap'>
            {grid?.log? Changelog(grid):[]}
        </div>
        </>
    )
}

export default TimeTable