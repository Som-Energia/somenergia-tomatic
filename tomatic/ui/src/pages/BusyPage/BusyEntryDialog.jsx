import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Stack from '@mui/material/Stack'
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import TextField from '@mui/material/TextField'
import RadioField from '../../components/RadioField'
import MultiCheckField from '../../components/MultiCheckField'
import Dialog from '../../components/ResponsiveDialog'
import Tomatic from '../../services/tomatic'

function TurnsEditor({ value, onChange, helperText, label }) {
  const options = Array.from(value).map((value, i) => {
    return {
      label: Tomatic.hourLabel(i),
    }
  })
  const translatedValues = Array.from(value).map((value) => value === '1')
  function update(index, checked) {
    onChange(
      value.substr(0, index) + (checked ? '1' : '0') + value.substr(index + 1),
    )
  }
  return (
    <MultiCheckField
      name={'turns'}
      row={false}
      helperText={helperText}
      label={label}
      value={translatedValues}
      onChange={update}
      options={options}
    />
  )
}

export default function BusyEntryDialog({ entry, setEntry, onApply, onClose }) {
  if (!entry) return
  const days = ['', 'dl', 'dm', 'dx', 'dj', 'dv']
  const hours = Tomatic.grid().hours
  const noTurn = '0'.repeat(hours.length - 1)
  function update(value) {
    setEntry({ ...entry, ...value })
  }
  function handleClose() {
    onClose && onClose()
  }
  function handleApply() {
    onApply && onApply(entry)
    onClose && onClose()
  }
  return (
    <Dialog open onClose={handleClose}>
      <DialogTitle>{'Edita indisponibilitat'}</DialogTitle>
      <DialogContent sx={{ minWidth: '40rem' }}>
        <Stack gap={2} marginTop={1}>
          <TextField
            autoFocus
            required
            label={'Motiu'}
            helperText={'Explica el motiu, com a referència'}
            value={entry.reason}
            onChange={(ev) => {
              update({ reason: ev.target.value })
            }}
          />
          {entry.weekday === undefined ? (
            <TextField
              type="date"
              label={'Dia'}
              helperText={'Escull el dia'}
              value={new Date(entry.date).toISOString().slice(0, 10)}
              onChange={(ev) =>
                update({
                  date: new Date(ev.target.value).toISOString().slice(0, 10),
                })
              }
            />
          ) : (
            <TextField
              select
              label={'Dia de la setmana'}
              helperText={'Escull el dia'}
              value={entry.weekday || 'tots'}
              onChange={(ev) =>
                update({
                  weekday: ev.target.value === 'tots' ? '' : ev.target.value,
                })
              }
            >
              {days.map((day, i) => (
                <MenuItem key={i} value={day || 'tots'}>
                  {day ? Tomatic.weekday(day) : 'Tots els dies'}
                </MenuItem>
              ))}
            </TextField>
          )}
          <RadioField
            name="optional"
            label={'Opcional'}
            helperText={'Es podria descartar, si estiguessim apurats?'}
            value={entry.optional ? 'yes' : 'no'}
            onChange={(ev, value) => {
              update({ optional: value === 'yes' })
            }}
            options={[
              {
                value: 'yes',
                label: 'Sí',
              },
              {
                value: 'no',
                label: 'No',
              },
            ]}
          />
          <TurnsEditor
            label={'Hores no disponibles'}
            value={entry.turns}
            onChange={(value) => update({ turns: value })}
            helperText={'Marca les hores en que no estaràs disponible'}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        {!entry.reason ? (
          <Alert severity="error">{'Cal posar un motiu'}</Alert>
        ) : entry.turns === noTurn ? (
          <Alert severity="warning">
            {'Sense marcar hores no tindra efecte'}
          </Alert>
        ) : !entry.optional ? (
          <Alert severity="warning">
            {'Segur que no la pots fer opcional?'}
          </Alert>
        ) : (
          <Alert sx={{ opacity: 0 }}>{'Tot ok'}</Alert>
        )}
        <div style={{ flex: 1 }}></div>
        <Button onClick={handleClose}>{'Cancel·la'}</Button>
        <Button
          variant="contained"
          disabled={!entry.reason}
          onClick={handleApply}
        >
          {'Desa'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
