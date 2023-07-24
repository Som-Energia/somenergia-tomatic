import React, { useState, useEffect } from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import TextField from '@mui/material/TextField'
import Select from '@mui/material/Select'
import MenuItem from '@mui/material/MenuItem'
import Autocomplete from '@mui/material/Autocomplete'
import Button from '@mui/material/Button'
import FormHelperText from '@mui/material/FormHelperText'
import FormControl from '@mui/material/FormControl'
import InputLabel from '@mui/material/InputLabel'
import Alert from '@mui/material/Alert'
import { MuiColorInput } from 'mui-color-input'

const fields = {
  id: {
    label: 'Identificador',
    help: 'Identificador que es fa servir internament.',
  },
  name: {
    label: 'Nom mostrat',
    help: 'Nom amb espais, accents, majúscules i el que calgui.',
  },
  email: {
    label: 'Adreça de correu',
    help: 'Correu oficial que tens a Som Energia.',
  },
  erpuser: {
    label: 'Usuari ERP',
    help: "Usuari amb el que entres a l'erp.",
  },
  idealload: {
    label: 'Càrrega de torns',
    help: 'Torns que farà normalment en una setmana de 5 dies laborals. En blanc si no fa atenció.',
  },
  extension: {
    label: 'Extensió',
    help: 'Extensió de telèfon assignada a la centraleta.',
  },
  table: {
    label: 'Taula',
    help: 'Posem a la gent propera a la mateixa taula per evitar torns amb cacofonies',
  },
  color: {
    label: 'Color',
    help: 'Color personal',
  },
}

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
  const { open, onClose, onSave, person, tables, allGroups } = props
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
  function setCheckedData(person) {
    setData(person)
    if (!person) return
    setErrors({
      ...errors,
      ...Object.fromEntries(
        Object.keys(validators).map((key) => {
          const validator = validators[key]
          return [key, validator(person[key])]
        })
      ),
    })
  }

  useEffect(() => {
    setCheckedData(
      person === undefined ? defaultData : person === {} ? defaultData : person
    )
  }, [person])

  const validators = {
    id: (value) => {
      if (!value) return "L'identificador és requisit"
      if (value.length < 3) return "L'identificador és massa curt"
      if (!value.match(/[a-z]{3,10}/))
        return "L'identificador nomes pot tenir lletres minuscules"
      return false
    },
    email: (value) => {
      if (value === undefined) return false
      if (value === '') return false
      if (!value.includes('@')) return 'Ha de ser una adreça de correu vàlida'
      return false
    },
    erpuser: (value) => {
      if (value === undefined) return false
      if (value.length === 0) return false
      if (!value.match('^[a-zA-Z]{3,10}$'))
        return "El nom d'usuari ERP és invàlid"
      return false
    },
    idealload: (value) => {
      if (value === undefined) return false
      if (value === '') return false
      if (isNaN(parseInt(value))) return 'Ha de ser un número'
      return false
    },
  }

  function updater(field) {
    return (ev) => {
      const newvalue = ev.target.value
      const validator = validators[field]
      if (validator !== undefined) {
        const validationError = validator(newvalue, data)
        setErrors({
          ...errors,
          [field]: validationError,
        })
      }
      setData({ ...data, [field]: newvalue })
    }
  }
  const fieldOptions = (field) => {
    return {
      id: field,
      label: fields[field].label,
      helperText: errors[field] || fields[field].help,
      error: !!errors[field],
      value: data[field] === undefined ? defaultData[field] : data[field],
      onChange: updater(field),
    }
  }

  const commonFieldOptions = {
    fullWidth: true,
    variant: 'standard',
    margin: 'dense',
  }
  const isNew = person?.id === undefined
  return (
    <Dialog
      open={open}
      aria-labelledby="person-editor-title"
      aria-describedby="person-editor-description"
      onClose={onClose}
    >
      <DialogTitle id="person-editor-title">
        {isNew
          ? 'Afegeix una persona nova'
          : 'Edita la informació de la persona'}
      </DialogTitle>
      <DialogContent>
        <TextField
          {...fieldOptions('id')}
          inputProps={{ pattern: '[a-z]{3,10}$' }}
          disabled={!isNew}
          autoFocus={isNew}
          required
          onInput={(ev) => {
            ev.target.value = inputFilter_ID(ev.target.value)
          }}
          {...commonFieldOptions}
        />
        <TextField
          required
          autoFocus={!isNew}
          {...fieldOptions('name')}
          {...commonFieldOptions}
        />
        <TextField
          type="email"
          {...fieldOptions('email')}
          {...commonFieldOptions}
        />
        <TextField
          {...fieldOptions('erpuser')}
          {...commonFieldOptions}
          onInput={(ev) =>
            (ev.target.value = inputFilter_erpuser(ev.target.value))
          }
          inputProps={{ pattern: '^[a-zA-Z]{3,10}$' }}
        />
        {/*
          onInput={(ev) =>
            (ev.target.value = inputFilter_numbers(ev.target.value))
          }
        */}
        <TextField
          {...fieldOptions('idealload')}
          {...commonFieldOptions}
          inputProps={{ pattern: '^[0-9]{0,2}$' }}
        />
        <TextField
          {...fieldOptions('extension')}
          onInput={(ev) =>
            (ev.target.value = inputFilter_numbers(ev.target.value))
          }
          inputProps={{ pattern: '^[0-9]{4}$' }}
          {...commonFieldOptions}
        />
        <FormControl {...commonFieldOptions}>
          <InputLabel id="table-label">{fields.table.label}</InputLabel>
          <Select
            id="table"
            labelId="table-label"
            label={fields.table.label}
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
          <FormHelperText>{fields['table'].help}</FormHelperText>
        </FormControl>
        <MuiColorInput
          id="color"
          value={'#' + (data.color || 'ffffff')}
          format="hex"
          onChange={(value) => {
            const field = 'color'
            const newvalue = value.replace(/^#/gm, '')
            setData({ ...data, [field]: newvalue })
          }}
          isAlphaHidden
          {...commonFieldOptions}
        ></MuiColorInput>
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
        {Object.values(errors).some((x) => x) ? (
          <Alert severity="error" sx={{ height: '55%' }}>
            {'Hi ha camps incorrectes'}
          </Alert>
        ) : null}
        <div style={{ flex: 1 }}></div>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          disabled={!Object.values(errors).every((error) => !error)}
          onClick={() => {
            onSave(person?.id, data)
          }}
        >
          {'Desar'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
