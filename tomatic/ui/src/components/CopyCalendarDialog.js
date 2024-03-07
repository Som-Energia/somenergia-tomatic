import * as React from 'react'
import Button from '@mui/material/Button'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Link from '@mui/material/Link'
import Box from '@mui/material/Box'
import Alert from '@mui/material/Alert'
import CopyButton from './CopyButton'

export function CopyCalendarDialog({ closeDialog, username }) {
  const url = window.location.origin + `/api/calendar/${username}`
  return (
    <>
      <DialogTitle>{'Exportar els torns al Google Calendar'}</DialogTitle>
      <DialogContent>
        <ul>
          <li>
            {'Còpia aquesta URL:'}
            <CopyButton text={url} />
            <Box
              sx={{
                fontFamily: 'monospace',
                whiteSpace: 'pre',
                m: 2,
                p: 0,
              }}
            >
              {url}
            </Box>
          </li>
          <li>
            Al{' '}
            <Link
              sx={{ color: 'primary' }}
              href="https://calendar.google.com"
              target="_blank"
            >
              Google Calendar
            </Link>
            , clicka el signe + de l'apartat "Altres calendaris"
          </li>
          <li>{'Selecciona l\'opcio del menú "Importa URL"'}</li>
          <li>{'Enganxa la url del calendari'}</li>
          <li>
            {
              'Els teus torns apareixeran com a esdeveniments en el color del nou calendari que has creat'
            }
          </li>
        </ul>
        <Alert severity="warning">
          {
            "Google pot trigar més d'un dia en sincronitzar els canvis que es vagin fent a les graelles."
          }
        </Alert>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" color="primary" onClick={closeDialog}>
          Tanca
        </Button>
      </DialogActions>
    </>
  )
}
