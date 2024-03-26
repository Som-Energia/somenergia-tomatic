import React from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Checkbox from '@mui/material/Checkbox'
import Stack from '@mui/material/Stack'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import FormHelperText from '@mui/material/FormHelperText'
import FormLabel from '@mui/material/FormLabel'
import FormControl from '@mui/material/FormControl'
import FormControlLabel from '@mui/material/FormControlLabel'
import RadioGroup from '@mui/material/RadioGroup'
import Radio from '@mui/material/Radio'
import MenuItem from '@mui/material/MenuItem'
import Alert from '@mui/material/Alert'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction'
import ListSubheader from '@mui/material/ListSubheader'
import IconButton from '@mui/material/IconButton'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import { useDialog } from './DialogProvider'
import Tomatic from '../services/tomatic'

function RadioField({
  name,
  variant = 'outlined',
  value,
  onChange,
  options,
  helperText,
  label,
}) {
  return (
    <FormControl variant={variant}>
      <FormLabel id={name + '-label'} variant={variant}>
        {label}
      </FormLabel>
      <RadioGroup
        row
        aria-labelledby={name + '-label'}
        name={name}
        value={value}
        onChange={onChange}
      >
        {options.map((option, i) => (
          <FormControlLabel control={<Radio />} key={i} {...option} />
        ))}
      </RadioGroup>
      <FormHelperText id={name + '-helper'}>{helperText}</FormHelperText>
    </FormControl>
  )
}

function TurnsDisplay({ turns }) {
  return (
    <span
      style={{
        color: '#a44',
        fontSize: '150%',
        marginInline: 'auto',
      }}
    >
      {Array.from(turns).map(function (e, i) {
        return (
          <React.Fragment key={i}>
            {e - 0 ? <>&#x2612;</> : <>&#x2610;</>}
          </React.Fragment>
        )
      })}
    </span>
  )
}

function TurnsEditor({
  name,
  variant = 'outlined',
  value,
  onChange,
  options,
  helperText,
  label,
}) {
  const hours = Tomatic.grid().hours
  return (
    <FormControl variant={variant}>
      <FormLabel id={name + '-label'} variant={variant}>
        {label}
      </FormLabel>
      {Array.from(value).map(function (active, i) {
        return (
          <FormControlLabel
            key={i}
            label={`${hours[i]} - ${hours[i + 1]}`}
            control={
              <Checkbox
                checked={active === '1'}
                onChange={(ev) =>
                  onChange(
                    value.substr(0, i) +
                      (ev.target.checked ? '1' : '0') +
                      value.substr(i + 1),
                  )
                }
              />
            }
          />
        )
      })}
      <FormHelperText id={name + '-helper'}>{helperText}</FormHelperText>
    </FormControl>
  )
}

function BusyEntryEditor({ entry, setEntry, onApply, onClose }) {
  if (!entry) return
  const days = ['', 'dl', 'dm', 'dx', 'dj', 'dv']
  function update(value) {
    setEntry({ ...entry, ...value })
  }
  return (
    <Dialog open>
      <DialogTitle>{'Edita indisponibilitat'}</DialogTitle>
      <DialogContent>
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
        {!entry.reason ? (
          <Alert severity="error">{'Cal posar un motiu'}</Alert>
        ) : entry.turns === '0000' ? (
          <Alert severity="warning">
            {'Sense marcar hores no tindra efecte'}
          </Alert>
        ) : !entry.optional ? (
          <Alert severity="warning">{'Segur que no es opcional?'}</Alert>
        ) : (
          <Alert sx={{ opacity: 0 }}>{'Tot ok'}</Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose && onClose()}>{'Cancel·la'}</Button>
        <Button
          variant="contained"
          disabled={!entry.reason}
          onClick={() => {
            onApply && onApply(entry)
            onClose && onClose()
          }}
        >
          {'Desa'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

function nextMonday(date) {
  var d = date || new Date()
  d.setDate(d.getDate() + 14 - ((6 + d.getDay()) % 7))
  return d.toISOString().substr(0, 10)
}

function BusyList({ title, entries, setEntries, isOneShot }) {
  const [entryToEdit, setEntryToEdit] = React.useState(undefined)
  const [onApply, setOnApply] = React.useState(undefined)

  function addEntry() {
    const newEntry = {
      weekday: isOneShot ? undefined : '',
      date: isOneShot ? nextMonday() : undefined,
      reason: '',
      optional: true,
      turns: '0000',
    }

    setEntryToEdit(newEntry)
    setOnApply(() => (entry) => {
      setEntries([...entries, entry])
    })
  }

  function editEntry(index) {
    setEntryToEdit({ ...entries[index] })
    setOnApply(() => (entry) => {
      const newEntries = [...entries]
      newEntries[index] = entry
      setEntries(newEntries)
    })
  }

  function removeEntry(index) {
    entries.splice(index, 1)
    setEntries([...entries])
  }

  return (
    <List
      sx={{
        maxWidth: '25rem',
      }}
    >
      <BusyEntryEditor
        entry={entryToEdit}
        setEntry={setEntryToEdit}
        onApply={onApply}
        onClose={() => setEntryToEdit(undefined)}
      />
      <ListSubheader>
        <Stack direction="row" justifyContent="space-between" gap={1}>
          {title}
          <div>
            <IconButton
              aria-label={'Afegeix nova indisponibilitat'}
              onClick={addEntry}
            >
              <AddIcon />
            </IconButton>
          </div>
        </Stack>
      </ListSubheader>
      {entries.map((entry, index) => {
        var day = entry.date || Tomatic.weekday(entry.weekday, 'Tots els dies')
        return (
          <ListItem
            key={index}
            button
            dense
            secondaryAction={
              <IconButton
                aria-label={'Esborra'}
                onClick={(ev) => {
                  removeEntry(index)
                  ev.stopPropagation()
                }}
              >
                <DeleteIcon />
              </IconButton>
            }
            onClick={() => editEntry(index)}
          >
            <ListItemIcon
              style={{
                transform: 'rotate(-45deg)',
                fontSize: '80%',
              }}
            >
              {entry.optional ? 'Opcional' : ''}
            </ListItemIcon>
            <ListItemText
              primary={
                <Stack direction="row" gap={3}>
                  <div>{day}</div>
                  <TurnsDisplay turns={entry.turns} />
                </Stack>
              }
              secondary={entry.reason || '--'}
            ></ListItemText>
          </ListItem>
        )
      })}
    </List>
  )
}

export default function BusyEditor({ name, data, setData }) {
  return (
    <>
      <h5>{`Indisponibilitats de ${name}`}</h5>
      <BusyList
        title={'Setmanals'}
        entries={data.weekly}
        setEntries={(entries) => setData({ ...data, weekly: entries })}
      />
      <BusyList
        title={'Puntuals'}
        entries={data.oneshot}
        setEntries={(entries) => setData({ ...data, oneshot: entries })}
        isOneShot
      />
    </>
  )
}
