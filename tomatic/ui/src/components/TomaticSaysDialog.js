import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'
import TextField from '@mui/material/TextField'
import Tomatic from '../services/tomatic'

export default function TomaticSaysDialog({ closeDialog }) {
  const [message, setPhoneNumber] = React.useState('')
  function submit() {
    Tomatic.says(message)
    closeDialog()
  }
  return (
    <>
      <DialogTitle>{'En Tomatic diu 📢'}</DialogTitle>
      <DialogContent>
        <Box sx={{ p: 2 }}>
          {'Envia missatges a les companyes impersonant al Tomatic. '}
        </Box>
        <TextField
          sx={{ flex: 1, minWidth: '15rem' }}
          multiline
          maxRows={4}
          required
          value={message}
          onChange={(e) => setPhoneNumber(e.target.value)}
          pattern="^\d{9}$"
          label={'Missatge'}
          helperText={'Pots fer servir Markdown per formatejar'}
          variant="standard"
          fullWidth
          autoFocus
        />
      </DialogContent>
      <DialogActions>
        <Button variant="contained" disabled={!message} onClick={submit}>
          {'Envia'}
        </Button>
      </DialogActions>
    </>
  )
}
