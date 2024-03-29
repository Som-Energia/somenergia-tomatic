import React from 'react'

import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import Button from '@mui/material/Button'
import PersonPicker from './PersonPicker'
import styled from '@emotion/styled'

import Tomatic from '../services/tomatic'

export default function CellEditDialog(props) {
  const { cell, onClose, handleChange } = props

  const setPerson = (name) => {
    handleChange(name, cell)
  }
  const CellItem = styled.span`
    text-align: center;
    padding: 0.5em 2em;
    margin-top: 1em;
  `
  return (
    <>
      <DialogTitle>{'Edita posició de la graella'}</DialogTitle>
      <div>{/* Hack to avoid removing the margin of the first content*/}</div>
      <DialogContent>
        <DialogContentText>
          {`${Tomatic.weekday(cell.day)} a les ` +
            `${Tomatic.grid().hours[cell.hour]}, ` +
            `línia ${cell.turn + 1}, ` +
            'la feia '}
          <CellItem className={'extension ' + cell.name}>
            {Tomatic.formatName(cell.name)}
          </CellItem>
          {'. Qui ho ha de fer?'}
        </DialogContentText>
      </DialogContent>
      <DialogContent>
        <PersonPicker onPick={setPerson} nobodyPickable="true"></PersonPicker>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" onClick={onClose}>
          Cancel·la
        </Button>
      </DialogActions>
    </>
  )
}
