import React, { useState } from 'react'

import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import Button from '@mui/material/Button'
import useMediaQuery from '@mui/material/useMediaQuery'
import { useTheme } from '@mui/material/styles'
import PersonPicker from './PersonPicker'
import styled from '@emotion/styled'

import Tomatic from '../services/tomatic'

function EditDialog(props) {
  const { open, onClose, data, handleChange } = props
  const theme = useTheme()
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'))

  const setPerson = (name) => {
    handleChange(name, data)
  }
  const CellItem = styled.span`
    label: name;
    text-align: center;
    padding: 0.5em 2em;
    margin-top: 1em;
  `
  return (
    <div>
      <Dialog
        open={open}
        onClose={onClose}
        fullWidth={true}
        maxWidth={'md'}
        fullScreen={fullScreen}
      >
        <DialogTitle>{'Edita posició de la graella'}</DialogTitle>
        <DialogContent sx={{ bg: 'green', mt: '0' }}>
          <DialogContentText>
            {Tomatic.weekday(data.day) +
              ' a les ' +
              Tomatic.grid().hours[data.hour] +
              ', línia ' +
              (data.turn + 1) +
              ', la feia '}{' '}
            <CellItem className={'extension ' + data.name}>
              {Tomatic.formatName(data.name)}
            </CellItem>{' '}
            {'. Qui ho ha de fer?'}
          </DialogContentText>
        </DialogContent>
        <DialogContent>
          <PersonPicker onPick={setPerson} nobodyPickable="true"></PersonPicker>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel·la</Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}

export default EditDialog
