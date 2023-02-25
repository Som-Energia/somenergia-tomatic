import React from 'react'
import TableEditor from './TableEditor'
import personData from '../persons.json'
import { contrast } from '../colorutils'

function compileData() {
  const result = {}

  function joinAttribute(result, attribute) {
    Object.entries(personData[attribute + 's']).forEach(
      ([identifier, v], i) => {
        if (!result[identifier]) result[identifier] = { identifier: identifier }
        result[identifier][attribute] = v
      }
    )
  }
  function joinGroups(result) {
    Object.entries(personData.groups).forEach(([group, members], i) => {
      members.forEach((member) => {
        if (result[member] === undefined) {
          result[member] = { identifier: member }
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

  return Object.entries(result).map(([identifier, v]) => {
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
    id: 'identifier',
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
          {row.name || camelize(row.identifier)}
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

