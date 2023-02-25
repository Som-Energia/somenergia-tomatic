import React from 'react'
import TableEditor from './TableEditor'
import personData from '../persons.json'
import { contrast } from '../colorutils'

function compileData() {
  const result = {}

  function joinAttribute(result, attribute) {
    Object.entries(personData[attribute + 's']).forEach(
      ([id, v], i) => {
        if (!result[id]) result[id] = { id: id }
        result[id][attribute] = v
      }
    )
  }
  function joinGroups(result) {
    Object.entries(personData.groups).forEach(([group, members], i) => {
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

const rows = compileData()

function camelize(text) {
  text = text.toLowerCase()
  return text.charAt(0).toUpperCase() + text.slice(1)
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
          {row.name || camelize(row.id)}
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
  },
]


function PersonsTable() {
  return <TableEditor 
    title={"Persones"}
    defaultPageSize={12}
    pageSizes={[12, 18, 25]}
    columns={columns}
    rows={rows}
  />
}

export default PersonsTable

