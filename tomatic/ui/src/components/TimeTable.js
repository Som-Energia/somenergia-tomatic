import React from 'react'
import Tomatic from '../services/tomatic'

import CellEditDialog from './CellEditDialog'
import Fab from '@mui/material/Fab'
import Stack from '@mui/material/Stack'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import Tooltip from '@mui/material/Tooltip'
import { useDialog } from './DialogProvider'

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

  const [openDialog, closeDialog] = useDialog()

  const handleChange = (name, data) => {
    setCell(data.day, data.hour, data.turn, name)
    closeDialog()
  }

  const handleClick = (day, houri, turni, name) => {
    const cellData = { day: day, hour: houri, turn: turni, name: name }
    openDialog({
      children: (
        <CellEditDialog
          cell={cellData}
          onClose={closeDialog}
          handleChange={handleChange}
        ></CellEditDialog>
      ),
      maxWidth: 'md',
    })
  }

  function cell(day, houri, turni) {
    var name = getCell(day, houri, turni)
    return (
      <td
        key={day + houri + turni}
        className={name}
        onClick={() => handleClick(day, houri, turni, name)}
      >
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
            .map((change, i) => (
              <li key={i}>{change}</li>
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
          {(grid.penalties || []).map((penalty, i) => (
            <li key={i}>{penalty[0] + ': ' + penalty[1]}</li>
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
          {Object.keys(grid.overload || {}).map((person, i) => (
            <li key={i}>{person + ': ' + grid.overload[person]}</li>
          ))}
        </ul>
      </div>
    )
  }

  return (
    <>
      {addColumn && removeColumn ? (
        <div>
          <Tooltip title="Afegir una línia">
            <Fab
              size="medium"
              color="primary"
              aria-label="add"
              position="TopRight"
              onClick={addColumn}
            >
              <AddIcon />
            </Fab>
          </Tooltip>
          <Tooltip title="Esborrar última línia">
            <Fab
              size="medium"
              color="primary"
              aria-label="remove"
              position="TopRight"
              onClick={removeColumn}
            >
              <RemoveIcon />
            </Fab>
          </Tooltip>
        </div>
      ) : null}
      <Stack
        direction="row"
        flexWrap="wrap"
        justifyContent="center"
        alignItems="center"
      >
        {(grid?.days || []).map((day) => (
          <div key={day} className="graella">
            <table>
              <thead>
                <tr>
                  <th>{Tomatic.weekday(day)}</th>
                  {grid?.turns.map((turn) => (
                    <th key={turn}>{turn}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {grid?.hours.slice(0, -1).map((hour, houri) => (
                  <tr key={hour}>
                    <th className="separator">{Tomatic.hourLabel(houri)}</th>
                    {grid.turns.map((turn, turni) => cell(day, houri, turni))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </Stack>
      <Stack
        direction="row"
        flexWrap="wrap"
        justifyContent="space-around"
        sx={{ '& > *': { flex: 1 } }}
      >
        {grid?.log ? Changelog(grid) : []}
        {grid?.penalties && showPenalties ? Penalties(grid) : []}
        {grid?.overload && showOverloads ? Overloads(grid) : []}
      </Stack>
    </>
  )
}

export default TimeTable
