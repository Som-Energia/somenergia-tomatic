import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Paper from '@mui/material/Paper'
import Dialog from '../../components/ResponsiveDialog'
import Tomatic from '../../services/tomatic'
import { TomaticBusyEditor } from './BusyEditor'

// A dialog to edit Busy info. Opens whenever person is set.
export default function BusyDialog({ person, setPerson }) {

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
        <Button variant="contained" onClick={handleClose}>
          {'Tanca'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

