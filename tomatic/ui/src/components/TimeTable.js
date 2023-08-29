import React, { useState, useEffect } from 'react'
import Tomatic from '../services/tomatic'

import PersonStyles from './PersonStyles'
import customStyle from '../mithril/style.styl'

import EditDialog from './EditDialog'
import Fab from '@mui/material/Fab'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import Tooltip from '@mui/material/Tooltip'

function TimeTable(props) {
  const {
    grid,
    setCell,
    getCell,
    addColumn,
    removeColumn,
    showPenalties,
    showOverloads,
  } = props

  const [dialogIsOpen, setDialogIsOpen] = useState(false)
  const [cellData, setCellData] = useState({})

  const openDialog = () => setDialogIsOpen(true)

  const closeDialog = () => setDialogIsOpen(false)

  const handleClick = (day, houri, turni, name) => {
    setCellData({ day: day, hour: houri, turn: turni, name: name })
    openDialog()
  }

  function cell(day, houri, turni) {
    var name = getCell(day, houri, turni)
    return (
      <td className={name} onClick={() => handleClick(day, houri, turni, name)}>
        {Tomatic.formatName(name)}
        <div className="tooltip">{Tomatic.formatExtension(name)}</div>
      </td>
    )
  }

  function Changelog(grid) {
    return (
      <div className="graella">
        <h5>Darrers canvis</h5>
        <ul className="changelog">
          {grid.log ? [] : <li>'Cap canvi registrat'</li>}
          {grid.log
            .slice(0, -1)
            .reverse()
            .map((change) => (
              <li>{change}</li>
            ))}
        </ul>
      </div>
    )
  }

  function Penalties(grid) {
    return (
      <div className="graella">
        <h5>Penalitzacions ({grid.cost || 0} punts)</h5>
        <ul className="penalties">
          {grid.penalties ? [] : <li>'La graella no te penalitzacions'</li>}
          {(grid.penalties || []).map((penalty) => (
            <li>{penalty[0] + ': ' + penalty[1]}</li>
          ))}
        </ul>
      </div>
    )
  }

  function Overloads(grid) {
    return (
      <div className="graella">
        <h5>Sobrecarrega respecte l'ideal</h5>
        <ul className="overloads">
          {grid.overload ? (
            []
          ) : (
            <li>'La graella no te sobrecarregues apuntades'</li>
          )}
          {Object.keys(grid.overload || {}).map((person) => (
            <li>{person + ': ' + grid.overload[person]}</li>
          ))}
        </ul>
      </div>
    )
  }

  const handleChange = (name, data) => {
    setCell(data.day, data.hour, data.turn, name)
    closeDialog()
  }

  function AddTurn() {
    addColumn()
  }

  function RemoveTurn() {
    removeColumn()
  }

  return (
    <>
      <PersonStyles />
      {dialogIsOpen ? (
        <EditDialog
          open={dialogIsOpen}
          data={cellData}
          handleChange={handleChange}
          onClose={closeDialog}
        ></EditDialog>
      ) : null}
      {addColumn && removeColumn ? (
        <div>
          <Tooltip title="Afegir una línia">
            <Fab
              size="medium"
              color="primary"
              aria-label="add"
              position="TopRight"
            >
              <AddIcon onClick={AddTurn} />
            </Fab>
          </Tooltip>
          <Tooltip title="Esborrar última línia">
            <Fab
              size="medium"
              color="primary"
              aria-label="remove"
              position="TopRight"
            >
              <RemoveIcon onClick={RemoveTurn} />
            </Fab>
          </Tooltip>
        </div>
      ) : null}
      <div className="layout center-center wrap">
        {(grid?.days || []).map((day) => (
          <div className="graella">
            <table>
              <thead>
                <tr>
                  <th>{Tomatic.weekday(day)}</th>
                  {grid?.turns.map((turn) => (
                    <td>{turn}</td>
                  ))}
                </tr>
              </thead>
              <tbody>
                {grid?.hours.slice(0, -1).map((hour, houri) => (
                  <tr key={hour}>
                    <th className="separator">
                      {grid?.hours[houri] + '-' + grid?.hours[houri + 1]}
                    </th>
                    {grid.turns.map((turn, turni) => cell(day, houri, turni))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
      <div className="layout.around-justified.wrap">
        {grid?.log ? Changelog(grid) : []}
        {grid?.penalties && showPenalties ? Penalties(grid) : []}
        {grid?.overload && showOverloads ? Overloads(grid) : []}
      </div>
    </>
  )
}

export default TimeTable
