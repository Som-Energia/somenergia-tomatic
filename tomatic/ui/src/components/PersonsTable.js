import React from 'react'
import TableEditor from './TableEditor'
import PersonEditor from './PersonEditor'
import Chip from '@mui/material/Chip'
import { contrast } from '../colorutils'
import EditIcon from '@mui/icons-material/Edit'
import EventBusyIcon from '@mui/icons-material/EventBusy'
import DeleteIcon from '@mui/icons-material/Delete'
import GroupAddIcon from '@mui/icons-material/GroupAdd'
import GroupRemoveIcon from '@mui/icons-material/GroupRemove'
import PersonAddIcon from '@mui/icons-material/PersonAdd'
import Tomatic from '../services/tomatic'

Tomatic.init()

function compileData(personData) {
  const result = {}
  if (personData === undefined) return {}

  function joinAttribute(result, attribute) {
    const attributeValues = personData[attribute + 's'] || {}
    Object.entries(attributeValues).forEach(([id, v], i) => {
      if (!result[id]) result[id] = { id: id }
      result[id][attribute] = v
    })
  }
  function joinGroups(result) {
    Object.entries(personData.groups || {}).forEach(([group, members], i) => {
      members.forEach((member) => {
        if (result[member] === undefined) {
          result[member] = { id: member }
        }
        if (result[member].groups === undefined) {
          result[member].groups = []
        }
        result[member].groups.push(group)
      })
    })
  }

  joinAttribute(result, 'name')
  joinAttribute(result, 'table')
  joinAttribute(result, 'extension')
  joinAttribute(result, 'color')
  joinAttribute(result, 'email')
  joinAttribute(result, 'erpuser')
  joinAttribute(result, 'load')
  joinGroups(result)

  return Object.entries(result).map(([id, v]) => {
    return v
  })
}

function range(end) {
  if (end < 1) return []
  return [...Array(end).keys()]
}

function formatName(row) {
  if (row.name) return row.name
  return camelize(row.id)
}

function availableTables(rows) {
  const tableMembers = rows.reduce((d, row) => {
    if (row.table === undefined) return d
    if (row.table === -1) return d
    if (d[row.table] === undefined) {
      d[row.table] = []
    }
    d[row.table].push(formatName(row))
    return d
  }, {})
  const result = [[-1, 'Sense taula']]
  const nTables = Math.max(...Object.keys(tableMembers))
  for (const i in range(nTables + 1)) {
    if (tableMembers[i] === undefined) {
      result.push([i, `Taula ${i} amb ningú`])
    } else {
      result.push([i, `Taula ${i} amb ` + tableMembers[i].join(', ')])
    }
  }
  return result
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
    id: 'load',
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

function availableGroups(rows) {
  return [
    ...new Set(
      rows
        .map((row) => {
          return row.groups || []
        })
        .flat()
    ),
  ]
}
function camelize(text) {
  text = text.toLowerCase()
  return text.charAt(0).toUpperCase() + text.slice(1)
}

var handlePersonsUpdated = () => {}

Tomatic.onPersonsUpdated.push(() => handlePersonsUpdated())

function PersonsTable() {
  const [rows, setRows] = React.useState([])
  const [tables, setTables] = React.useState([])
  const [groups, setGroups] = React.useState([])
  const [editingPerson, setEditingPerson] = React.useState(undefined)

  handlePersonsUpdated = () => {
    const persons = Tomatic.persons()
    console.log('Redrawing persons', persons)
    const rows = compileData(persons)
    setRows(rows)
    setTables(availableTables(rows))
    setGroups(availableGroups(rows))
  }

  function handleStartAddingPerson() {
    setEditingPerson({})
  }
  function handleStartEditingPerson(person) {
    setEditingPerson(person)
  }
  function handleEndEditingPerson() {
    setEditingPerson(undefined)
  }
  function handleSavePerson(id, data) {
    console.log(id, data)
    Tomatic.setPersonDataReact(id, data)
    setEditingPerson(undefined)
  }

  const actions = [
    {
      title: 'Add Person',
      icon: <PersonAddIcon />,
      handler: handleStartAddingPerson,
    },
  ]
  const selectionActions = [
    {
      title: 'Add to Group',
      icon: <GroupAddIcon />,
    },
    {
      title: 'Remove from Grou',
      icon: <GroupRemoveIcon />,
    },
    {
      title: 'Remove Person',
      icon: <DeleteIcon />,
    },
  ]

  const itemActions = [
    {
      title: 'Edit',
      icon: <EditIcon fontSize="inherit" />,
      handler: handleStartEditingPerson,
    },
    {
      title: 'Indisponibilitats',
      icon: <EventBusyIcon fontSize="inherit" />,
    },
  ]

  return (
    <>
      <TableEditor
        title={'Persones'}
        defaultPageSize={12}
        pageSizes={[12, 18, 25]}
        columns={columns}
        rows={rows}
        actions={actions}
        selectionActions={selectionActions}
        itemActions={itemActions}
      ></TableEditor>
      <PersonEditor
        open={editingPerson !== undefined}
        onClose={handleEndEditingPerson}
        onSave={handleSavePerson}
        disableEscapeKeyDown={false}
        person={editingPerson}
        allGroups={groups}
        tables={tables}
      />
    </>
  )
}

export default PersonsTable
