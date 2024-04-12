import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
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
  const isAdmin = Tomatic.belongsToGroup(userid, 'admin s')
  const isValid = /^\d{3}$/.test(extension) && /^\d{9}$/.test(phoneNumber)
  function submit() {
    CallInfo.emulateCall(phoneNumber, extension)
    closeDialog()
  }
  return (
    <>
      <DialogTitle>{'Emulador de trucada entrant 🤙'}</DialogTitle>
      <DialogContent>
        <Box sx={{ p: 2 }}>
          {'Eina per fer proves. ' +
            'Afegirà una trucada entrant al registre i encetarà una cerca, com si vingués de la Centraleta.'}
        </Box>
        <Stack direction="row" gap={2} flexWrap="wrap">
          <TextField
            sx={{ flex: 1, minWidth: '15rem' }}
            select
            fullWidth
            required
            value={extension}
            onChange={(e) => setExtension(e.target.value)}
            label={'Extensió'}
            helperText={"Operadora a la que s'envia la trucada"}
            variant="standard"
          >
            {Object.keys(Tomatic.persons().extensions).map((name) => (
              <MenuItem
                key={name}
                value={Tomatic.persons().extensions[name]}
                disabled={!isAdmin && name !== userid}
              >
                {`${Tomatic.formatExtension(name)} - ${Tomatic.formatName(
                  name,
                )}`}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            sx={{ flex: 1, minWidth: '15rem' }}
            required
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            pattern="^\d{9}$"
            label={'Número de telèfon'}
            helperText={'Qui simulem que ens truca'}
            variant="standard"
            fullWidth
            autoFocus
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        {isValid ? (
          <Alert sx={{ opacity: 0 }}>{'Tot correcte'}</Alert>
        ) : (
          <Alert severity="error">
            {'El número de telèfon ha de tenir 9 dígits'}
          </Alert>
        )}
        <Box sx={{ flex: 1 }} />
        <Button onClick={closeDialog}>{'Cancel·la'}</Button>
        <Button variant="contained" disabled={!isValid} onClick={submit}>
          {'Simula trucada'}
        </Button>
      </DialogActions>
    </>
  )
}
