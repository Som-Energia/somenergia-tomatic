import * as React from 'react'
import Button from '@mui/material/Button'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'

export function CopyCalendarDialog({ closeDialog, username }) {
  return (
    <>
      <DialogTitle>{'Exportar els torns al Google Calendar'}</DialogTitle>
      <DialogContent>
        <ul>
          <li>
            {'Còpia la següent URL'}
            <pre>{`https://tomatic.somenergia.coop/api/calendar/${username}`}</pre>
          </li>
          <li>
            {
              'Al Google Calendar, clicka el signe + de l\'apartat "Altres calendaris"'
            }
          </li>
          <li>{'Selecciona l\'opcio del menú "Importa URL"'}</li>
          <li>{'Enganxa la url del calendari'}</li>
          <li>
            {
              'Els teus torns apareixeran com a esdeveniments en el color del nou calendari nou que has creat'
            }
          </li>
        </ul>
        <h6>Atenció</h6>
        <ul>
          <li>
            {'Google només sincronitza cada 24h el calendari. ' +
              'No reflexarà inmediatament els canvis fets al Tomàtic.'}
          </li>
        </ul>
      </DialogContent>
      <DialogActions>
        <Button color="primary" onClick={closeDialog}>
          Tanca
        </Button>
      </DialogActions>
    </>
  )
}
