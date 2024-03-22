import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import TextField from '@mui/material/TextField'
import Stack from '@mui/material/Stack'
import AuthContext from '../contexts/AuthContext'
import Tomatic from '../services/tomatic'
import CallInfo from '../mithril/components/callinfo'

export default function EmulateCallDialog({ closeDialog }) {
  const { userid } = React.useContext(AuthContext)
  const [extension, setExtension] = React.useState(
    () => Tomatic.persons().extensions[userid],
  )
  const [phoneNumber, setPhoneNumber] = React.useState('')

  const isValid = /^\d{3}$/.test(extension) && /^\d{9}$/.test(phoneNumber)
  function submit() {
    CallInfo.emulateCall(phoneNumber, extension)
    closeDialog()
  }
  return (
    <>
      <DialogTitle>{'Emula trucada entrant'}</DialogTitle>
      <DialogContent>
        <Stack gap={2}>
          <TextField
            disabled
            value={extension}
            onChange={(e) => setExtension(e.target.value)}
            label={'Extensió'}
            variant="standard"
            fullWidth
            rows={4}
          />
          <TextField
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            pattern="^\d{9}$"
            label={'Número de telèfon'}
            variant="standard"
            fullWidth
            rows={4}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={closeDialog}>{'Cancel·la'}</Button>
        <Button variant="contained" disabled={!isValid} onClick={submit}>
          {'Simula trucada'}
        </Button>
      </DialogActions>
    </>
  )
}
