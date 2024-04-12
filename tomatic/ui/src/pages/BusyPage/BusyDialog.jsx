import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'
import Popover from '@mui/material/Popover'
import Dialog from '../../components/ResponsiveDialog'
import Tomatic from '../../services/tomatic'
import { TomaticBusyEditor } from './BusyEditor'
import BusyNotes from './BusyNotes'

// A dialog to edit Busy info. Opens whenever person is set.
export default function BusyDialog({ person, setPerson }) {
  const [popoverTarget, setOpenPopover] = React.useState(null)
  function handleClose() {
    setPerson(null)
  }

  if (!person) return
  const fullName = Tomatic.formatName(person)
  return (
    <Dialog open onClose={handleClose}>
      <DialogTitle>{`Edita indisponibilitat - ${fullName}`}</DialogTitle>
      <DialogContent>
        <TomaticBusyEditor person={person} />
      </DialogContent>
      <DialogActions>
        <Popover
          open={!!popoverTarget}
          onClose={() => setOpenPopover(null)}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
        >
          <BusyNotes />
        </Popover>
        <Button onClick={(ev) => setOpenPopover(ev.target)}>
          {'Com fer servir les indisponibilitats'}
        </Button>
        <Box flex={1} />
        <Button variant="contained" onClick={handleClose}>
          {'Tanca'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
