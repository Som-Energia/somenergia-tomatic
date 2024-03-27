import React from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import MenuItem from '@mui/material/MenuItem'
import Alert from '@mui/material/Alert'
import Typography from '@mui/material/Typography'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import ListSubheader from '@mui/material/ListSubheader'
import CircularProgress from '@mui/material/CircularProgress'
import IconButton from '@mui/material/IconButton'
import useMediaQuery from '@mui/material/useMediaQuery'
import { useTheme } from '@mui/material/styles'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import RadioField from '../../components/RadioField'
import MultiCheckField from '../../components/MultiCheckField'
import Tomatic from '../../services/tomatic'

function TurnsDisplay({ turns }) {
  return (
    <Typography
      sx={{
        color: '#a44',
        fontSize: '150%',
      }}
    >
      {Array.from(turns).map(function (e, i) {
        return (
          <React.Fragment key={i}>
            {e - 0 ? <>&#x2612;</> : <>&#x2610;</>}
          </React.Fragment>
        )
      })}
    </Typography>
  )
}

function TurnsEditor({ value, onChange, helperText, label }) {
  const hours = Tomatic.grid().hours
  const options = Array.from(value).map((value, i) => {
    return {
      label: `${hours[i]} - ${hours[i + 1]}`,
    }
  })
  const translatedValues = Array.from(value).map(
    (value) => value === '1'
  )
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

function BusyEntryDialog({ entry, setEntry, onApply, onClose }) {
  const theme = useTheme()
  const fullScreen = useMediaQuery(theme.breakpoints.down('sm'))
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
    <Dialog open fullScreen={fullScreen} scroll="paper" onClose={handleClose}>
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

function nextMonday(date) {
  var d = date || new Date()
  d.setDate(d.getDate() + 14 - ((6 + d.getDay()) % 7))
  return d.toISOString().substr(0, 10)
}

function BusyListItem({ entry, onRemove, onEdit }) {
  var day = entry.date || Tomatic.weekday(entry.weekday, 'Tots els dies')
  return (
    <ListItem
      button
      dense
      secondaryAction={
        <IconButton
          aria-label={'Esborra'}
          onClick={(ev) => {
            onRemove()
            ev.stopPropagation()
          }}
        >
          <DeleteIcon />
        </IconButton>
      }
      onClick={onEdit}
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
          <Stack direction="row" justifyContent="space-between" gap={1} mr={3}>
            <Typography>{day}</Typography>
            <TurnsDisplay turns={entry.turns} />
          </Stack>
        }
        secondary={
          <Typography variant="body2" noWrap>
            {entry.reason || '--'}
          </Typography>
        }
      ></ListItemText>
    </ListItem>
  )
}

function BusyList({ title, entries, setEntries, isOneShot }) {
  const [entryToEdit, setEntryToEdit] = React.useState(undefined)
  const [onApply, setOnApply] = React.useState(undefined)

  function addEntry() {
    const hours = Tomatic.grid().hours
    const noTurn = '0'.repeat(hours.length - 1)
    const newEntry = {
      weekday: isOneShot ? undefined : '',
      date: isOneShot ? nextMonday() : undefined,
      reason: '',
      optional: true,
      turns: noTurn,
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
        minWidth: '20rem',
        flex: 1,
      }}
    >
      <BusyEntryDialog
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
              disabled={!entries}
              aria-label={'Afegeix nova indisponibilitat'}
              onClick={addEntry}
            >
              <AddIcon />
            </IconButton>
          </div>
        </Stack>
      </ListSubheader>
      {entries === undefined ? (
        <>
          <ListItem sx={{justifyContent: 'center'}}>
            <CircularProgress />
          </ListItem>
          <ListItem sx={{justifyContent: 'center'}}>{'Obtenint dades...'}</ListItem>
        </>
      ) : entries.length === 0 ? (
        <ListItem sx={{justifyContent: 'center'}}>{"No n'heu establert cap"}</ListItem>
      ) : null}
      {entries &&
        entries.map((entry, index) => (
          <BusyListItem
            key={index}
            entry={entry}
            onRemove={() => removeEntry(index)}
            onEdit={() => editEntry(index)}
          />
        ))}
    </List>
  )
}

/// BusyEditor source agnostic
export default function BusyEditor({ data, setData }) {
  return (
    <Stack
      gap={1}
      direction="row"
      flexWrap="wrap"
      justifyContent="space-evenly"
      alignItems="top"
    >
      <BusyList
        title={'Setmanals'}
        entries={data?.weekly}
        setEntries={(entries) => setData({ ...data, weekly: entries })}
      />
      <BusyList
        title={'Puntuals'}
        entries={data?.oneshot}
        setEntries={(entries) => setData({ ...data, oneshot: entries })}
        isOneShot
      />
    </Stack>
  )
}

/// Busy editor taking data from Tomatic
export function TomaticBusyEditor({ person }) {
  const [data, setData] = React.useState(null)

  function updateData(newData) {
    setData(newData)
    Tomatic.sendBusyData(person, newData)
  }

  React.useEffect(() => {
    setData(null)
    Tomatic.retrieveBusyData(person, (data) => {
      setData(data)
    })
  }, [person])
  return <BusyEditor data={data} setData={updateData} />
}

// A dialog to edit Busy info. Opens whenever person is set.
export function BusyDialog({ person, setPerson }) {
  const theme = useTheme()
  const fullScreen = useMediaQuery(theme.breakpoints.down('sm'))

  function handleClose() {
    setPerson(null)
  }

  if (!person) return
  const fullName = Tomatic.formatName(person)
  return (
    <Dialog open fullScreen={fullScreen} scroll="paper" onClose={handleClose}>
      <DialogTitle>{`Edita indisponibilitat - ${fullName}`}</DialogTitle>
      <DialogContent>
        <Paper>
          <TomaticBusyEditor person={person} />
        </Paper>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" onClick={handleClose}>
          {'Tanca'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
