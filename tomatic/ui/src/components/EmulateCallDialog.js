import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'
import Alert from '@mui/material/Alert'
import TextField from '@mui/material/TextField'
import Stack from '@mui/material/Stack'
import AuthContext from '../contexts/AuthContext'
import Tomatic from '../services/tomatic'
import CallInfo from '../contexts/callinfo'

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
          <Box sx={{ p: 2 }}>
            {
              'Eina de proves que simula una trucada entrant com si vingués de la Centraleta.'
            }
          </Box>
          <TextField
            disabled
            required
            value={extension}
            onChange={(e) => setExtension(e.target.value)}
            label={'Extensió'}
            variant="standard"
            fullWidth
            rows={4}
          />
          <TextField
            required
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            pattern="^\d{9}$"
            label={'Número de telèfon'}
            variant="standard"
            fullWidth
            rows={4}
            autoFocus
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        {isValid ? (
          <Alert sx={{opacity:0}}>{'Tot correcte'}</Alert>
        ) : (
          <Alert severity="error">
            {'El número de telèfon ha de tenir 9 dígits'}
          </Alert>
        )}
        <Box sx={{flex: 1}}/>
        <Button onClick={closeDialog}>{'Cancel·la'}</Button>
        <Button variant="contained" disabled={!isValid} onClick={submit}>
          {'Simula trucada'}
        </Button>
      </DialogActions>
    </>
  )
}
