import React from 'react'
import Box from '@mui/material/Box'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import PersonPicker from '../../components/PersonPicker'
import { useDialog } from '../../components/DialogProvider'
import { useSubscriptable } from '../../services/subscriptable'
import Tomatic from '../../services/tomatic'

export default function QueueMonitor() {
  const [openDialog, closeDialog] = useDialog()
  const queue = useSubscriptable(Tomatic.queue)
  function addAgent() {
    openDialog({
      children: (
        <>
          <DialogTitle>{'Obre una nova línia amb:'}</DialogTitle>
          <DialogContent>
            <PersonPicker
              onPick={(name) => {
                Tomatic.addLine(name)
                closeDialog()
              }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={closeDialog}>{'Tanca'}</Button>
          </DialogActions>
        </>
      ),
    })
  }

  return (
    <Box className="queueeditor">
      {queue.map((line) => {
        return (
          <Box
            className={[
              'queueitem',
              line.key,
              line.paused ? 'paused' : 'resumed',
              line.disconnected ? 'disconnected' : '',
              line.ringing ? 'ringing' : '',
              line.incall ? 'incall' : '',
            ]}
            onClick={() =>
              line.paused
                ? Tomatic.restoreLine(line.key)
                : Tomatic.pauseLine(line.key)
            }
            key={line.key}
            title={
                (line.paused ? 'Pausada. ' : '') +
                (line.disconnected ? 'Desconnectada. ' : '') +
                (line.ringing ? 'Ring!! ' : '') +
                (line.incall ? 'En Trucada. ' : '') || 'Disponible. '
            }
          >
            {Tomatic.formatName(line.key)}
            <br />
            {Tomatic.formatExtension(line.key)}
          </Box>
        )
      })}
      <Box className="queueitem add" onClick={addAgent}>
        {'+'}
        <br />
        {'Afegeix'}
      </Box>
    </Box>
  )
}