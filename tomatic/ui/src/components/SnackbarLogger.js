import * as React from 'react'
import Snackbar from '@mui/material/Snackbar'
import Alert from '@mui/material/Alert'
import Tomatic from '../services/tomatic'

const Logger = {
  log: (msg) => {},
  error: (msg) => {},
}

Tomatic.loggers.push(Logger)

export default function SnackbarLogger() {
  const [open, setOpen] = React.useState(false)
  const [isError, beError] = React.useState(false)
  const [message, setMessage] = React.useState('')

  Logger.log = (message) => {
    setOpen(true)
    beError(false)
    setMessage(message)
  }
  Logger.error = (message) => {
    setOpen(true)
    beError(true)
    setMessage(message)
  }

  return (
    <Snackbar
      open={open}
      onClose={() => {
        setOpen(false)
      }}
      autoHideDuration={6000}
    >
      <Alert
        severity={isError ? 'error' : 'info'}
        onClose={() => {
          setOpen(false)
        }}
      >
        {message}
      </Alert>
    </Snackbar>
  )
}
