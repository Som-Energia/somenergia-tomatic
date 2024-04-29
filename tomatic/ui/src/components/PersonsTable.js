// PersonsTable: A table to browse and edit Persons info
import React from 'react'
import TableEditor from './TableEditor'
import PersonEditor from './PersonEditor'
import Chip from '@mui/material/Chip'
import Box from '@mui/material/Box'
import DialogContent from '@mui/material/DialogContent'
import Button from '@mui/material/Button'
import DialogTitle from '@mui/material/DialogTitle'
import DialogActions from '@mui/material/DialogActions'
import EditIcon from '@mui/icons-material/Edit'
import EventBusyIcon from '@mui/icons-material/EventBusy'
import DeleteIcon from '@mui/icons-material/Delete'
//import GroupAddIcon from '@mui/icons-material/GroupAdd'
//import GroupRemoveIcon from '@mui/icons-material/GroupRemove'
import PersonAddIcon from '@mui/icons-material/PersonAdd'
import Tomatic from '../services/tomatic'
import BusyDialog from '../pages/BusyPage/BusyDialog'
import { useDialog } from './DialogProvider'
import { contrast } from '../services/colorutils'

function formatName(row) {
  if (row.name) return row.name
  return camelize(row.id)
}

const columns = [
  {
    id: 'id',
    numeric: false,
    disablePadding: true,
    label: 'Identificador',
  },
  {
    id: 'name',
    label: 'Nom / Color',
    numeric: false,
    disablePadding: false,
    searchable: true,
    view: (row) => {
      const bg = row.color || 'aaaaee'
      const fg = contrast(bg)
      return (
        <div
          style={{
            padding: '5px',
            backgroundColor: `#${bg}`,
            color: `${fg}`,
            border: `1pt solid ${fg}`,
            textAlign: 'center',
          }}
        >
          {formatName(row)}
        </div>
      )
    },
  },
  {
    id: 'extension',
    label: 'Extensió',
    numeric: false,
    disablePadding: false,
    searchable: true,
  },
  {
    id: 'email',
    label: 'Correu Electrònic',
    numeric: true,
    disablePadding: false,
    searchable: true,
  },
  {
    id: 'erpuser',
    label: 'Usuaria ERP',
    numeric: false,
    disablePadding: false,
    searchable: true,
  },
  {
    id: 'idealload',
    label: 'Torns',
    numeric: true,
    disablePadding: false,
    searchable: true,
  },
  {
    id: 'table',
    numeric: true,
    disablePadding: false,
    label: 'Taula',
    view: (row) => (row.table === -1 ? '-' : row.table),
  },
  {
    id: 'groups',
    label: 'Grups',
    numeric: true,
    disablePadding: false,
    searchable: true,
    view: (row) =>
      row.groups &&
      row.groups.map((group) => {
        return <Chip key={group} size="small" label={group} />
      }),
  },
]

function camelize(text) {
  text = text.toLowerCase()
  return text.charAt(0).toUpperCase() + text.slice(1)
}

function PersonsTable() {
  const [openDialog, closeDialog] = useDialog()
  const [personToEditBusy, setPersonToEditBusy] = React.useState(null)
  const persons = Tomatic.persons.use()
  // All three need to update on persons. Use && to silence the linter
  const rows = React.useMemo(
    () => persons && Tomatic.allPeopleData(),
    [persons],
  )
  const tables = React.useMemo(
    () => persons && Tomatic.tableOptions(),
    [persons],
  )
  const groups = React.useMemo(() => persons && Tomatic.allGroups(), [persons])

  function deletePersons(persons) {
    openDialog({
      children: (
        <>
          <DialogTitle>
            {'Estas segur que vols eliminar els usuaris?'}
          </DialogTitle>
          <DialogContent
            sx={{
              width: '100%',
              display: 'flex',
              flex: 'row wrap',
              contentAlign: 'center',
            }}
          >
            {persons.map((person) => (
              <Box
                className={person}
                key={person}
                sx={{ width: '10rem', p: 1.2, m: 1, textAlign: 'center' }}
              >
                {person}
              </Box>
            ))}
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => {
                closeDialog()
              }}
            >
              {'Ui, NO! Espera! espera!'}
            </Button>
            <Button
              color="error"
              variant="contained"
              onClick={() => {
                persons.forEach((person) => Tomatic.deletePerson(person))
                closeDialog()
              }}
            >
              {'Clar que sí, fora!'}
            </Button>
          </DialogActions>
        </>
      ),
    })
  }

  function editPerson(person) {
    openDialog({
      children: (
        <PersonEditor
          onClose={closeDialog}
          onSave={(id, data) => {
            Tomatic.setPersonDataReact(id, data)
            closeDialog()
          }}
          person={person}
          allGroups={groups}
          tables={tables}
        />
      ),
    })
  }

  function handleStartBusyEditor(person) {
    setPersonToEditBusy(person.id)
  }

  const actions = [
    {
      title: 'Add Person',
      icon: <PersonAddIcon />,
      handler: editPerson,
    },
  ]
  const selectionActions = [
    /*
    // TODO: Not implemented yet
    {
      title: 'Add to Group',
      icon: <GroupAddIcon />,
    },
    {
      title: 'Remove from Group',
      icon: <GroupRemoveIcon />,
    },
    */
    {
      title: 'Remove Person',
      icon: <DeleteIcon />,
      handler: deletePersons,
    },
  ]

  const itemActions = [
    {
      title: 'Edit',
      icon: <EditIcon fontSize="inherit" />,
      handler: editPerson,
    },
    {
      title: 'Indisponibilitats',
      icon: <EventBusyIcon fontSize="inherit" />,
      handler: handleStartBusyEditor,
    },
  ]

  return (
    <>
      <TableEditor
        title={'Persones'}
        defaultPageSize={-1}
        columns={columns}
        rows={rows}
        actions={actions}
        selectionActions={selectionActions}
        itemActions={itemActions}
        pageSizes={[-1]}
      ></TableEditor>
      <BusyDialog person={personToEditBusy} setPerson={setPersonToEditBusy} />
    </>
  )
}

export default PersonsTable
