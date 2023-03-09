import React, { useState, useEffect } from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogActions from '@mui/material/DialogActions'
import TextField from '@mui/material/TextField'
import Select from '@mui/material/Select'
import MenuItem from '@mui/material/MenuItem'
import Autocomplete from '@mui/material/Autocomplete'
import Button from '@mui/material/Button'

function inputFilter_ID(value) {
  return value
    .toLowerCase()
    .replace(/[óòôö]/g, 'o')
    .replace(/[àáâä]/g, 'a')
    .replace(/[íìîï]/g, 'i')
    .replace(/[úûûü]/g, 'u')
    .replace(/[éèêë]/g, 'e')
    .replace(/[ç]/g, 'c')
    .replace(/[ñ]/g, 'n')
    .replace(/[^a-z]/g, '')
    .slice(0, 10)
}
function inputFilter_numbers(value) {
  return value.replace(/[^0-9]/g, '')
}

function inputFilter_erpuser(value) {
  return value.replace(/[^A-Za-z]/g, '')
}

const defaultData = {
  id: '',
  name: '',
  email: '',
  erpuser: '',
  table: -1,
  extension: '',
  color: 'aaaaff',
  groups: [],
}

export default function PersonEditor(props) {
  const { open, onClose, person, tables, allGroups } = props
  const [data, setData] = useState(defaultData)
  const [errors, setErrors] = useState({
    id: false,
    name: false,
    email: false,
    erpuser: false,
    table: false,
    extension: false,
    color: false,
    groups: false,
  })
  useEffect(() => {
    if (person === undefined) {
      setData(defaultData)
    } else if (person === {}) {
      setData(defaultData)
    } else setData(person)
  }, [person, defaultData])

  const validators = {
    email: (value) => {
      if (!value.includes('@')) return 'Ha de ser una adreça de correu vàlida'
      return false
    },
  }

  console.log('data', data)
  function updater(field) {
    return (ev) => {
      const newvalue = ev.target.value
      const validator = validators[field]
      if (validator) {
        setErrors({
          ...errors,
          [field]: validator(newvalue, data),
        })
      }
      setData({ ...data, [field]: newvalue })
    }
  }
  console.log('errors', errors)
  const attributeOptions = (attribute) => {
    return {
      id: attribute,
      error: !!errors[attribute],
      value:
        data[attribute] === undefined
          ? defaultData[attribute]
          : data[attribute],
      onChange: updater(attribute),
    }
  }

  const commonFieldOptions = {
    fullWidth: true,
    variant: 'standard',
    margin: 'dense',
  }
  return (
    <Dialog
      open={open}
      aria-labelledby="person-editor-title"
      aria-describedby="person-editor-description"
      onClose={onClose}
    >
      <DialogTitle id="person-editor-title">Adding a person</DialogTitle>
      <DialogContent>
        <DialogContentText id="person-editor-description">
          {'Informació de la usuaria'}
        </DialogContentText>
        <TextField
          {...attributeOptions('id')}
          label="Identificador"
          helperText="Identificador que es fa servir internament."
          aerror="De 3 a 10 carácters. Només lletres en minúscules."
          inputProps={{ pattern: '[a-z]{3,10}$' }}
          disabled={person !== {}}
          autoFocus={person === {}}
          required
          onInput={(ev) => {
            ev.target.value = inputFilter_ID(ev.target.value)
          }}
          {...commonFieldOptions}
        />
        <TextField
          {...attributeOptions('name')}
          label="Nom mostrat"
          helperText="Nom amb accents, majúscules..."
          required
          autoFocus={person !== {}}
          {...commonFieldOptions}
        />
        <TextField
          {...attributeOptions('email')}
          label="Adreça de correu"
          helperText="Correu oficial que tens a Som Energia."
          type="email"
          {...commonFieldOptions}
        />
        <TextField
          {...attributeOptions('erpuser')}
          label="Usuari ERP"
          helperText="Usuari amb el que entres a l'erp."
          onInput={(ev) =>
            (ev.target.value = inputFilter_erpuser(ev.target.value))
          }
          inputProps={{ pattern: '^[a-zA-Z]{3,10}$' }}
          {...commonFieldOptions}
        />
        <TextField
          {...attributeOptions('load')}
          label="Càrrega de torns"
          helperText="Torns que farà normalment en una setmana de 5 dies. En blanc si no fa atenció."
          onInput={(ev) =>
            (ev.target.value = inputFilter_numbers(ev.target.value))
          }
          inputProps={{ pattern: '^[0-9]{0,10}$' }}
          {...commonFieldOptions}
        />
        <TextField
          {...attributeOptions('extension')}
          label="Extensió"
          helperText="Extensió de telèfon assignada a la centraleta."
          onInput={(ev) =>
            (ev.target.value = inputFilter_numbers(ev.target.value))
          }
          inputProps={{ pattern: '^[0-9]{4}$' }}
          {...commonFieldOptions}
        />
        <Select
          id="table"
          label="Taula"
          labelId="table-label"
          value={data.table === undefined ? -1 : data.table}
          onChange={updater('table')}
          {...commonFieldOptions}
        >
          {tables.map(([value, description]) => {
            return (
              <MenuItem key={value} value={value}>
                {description}
              </MenuItem>
            )
          })}
        </Select>
        {/* TODO: Use a color picker */}
        <TextField
          id="color"
          label="Color"
          helperText="Color personal"
          errorText="que color mas cutre"
          value={data.color || 'ffffff'}
          onChange={updater('color')}
          inputProps={{ pattern: '^[0-9a-f]{4}$' }}
          {...commonFieldOptions}
        ></TextField>
        <Autocomplete
          id="groups"
          multiple
          freeSolo
          options={allGroups}
          getOptionLabel={(option) => option}
          value={data.groups || []}
          onChange={(ev, newvalue) => setData({ ...data, groups: newvalue })}
          renderInput={(params) => (
            <TextField {...params} label="Group" {...commonFieldOptions} />
          )}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onClose}>
          {'Desar'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
