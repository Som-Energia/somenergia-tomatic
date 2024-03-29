import React from 'react'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import ListSubheader from '@mui/material/ListSubheader'
import CircularProgress from '@mui/material/CircularProgress'
import IconButton from '@mui/material/IconButton'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import Tomatic from '../../services/tomatic'
import BusyEntryDialog from './BusyEntryDialog'

function TurnsDisplay({ turns }) {
  return (
    <Typography
      sx={{
        color: 'secondary.main',
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
            <Typography color="primary">{day}</Typography>
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
          <ListItem sx={{ justifyContent: 'center' }}>
            <CircularProgress />
          </ListItem>
          <ListItem sx={{ justifyContent: 'center' }}>
            {'Obtenint dades...'}
          </ListItem>
        </>
      ) : entries.length === 0 ? (
        <ListItem sx={{ justifyContent: 'center' }}>
          {"No n'heu establert cap"}
        </ListItem>
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

