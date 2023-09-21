import React from 'react'
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
function inputFilter_onlyDigits(value) {
  return value.replace(/[^0-9]/g, '')
}

function inputFilter_erpuser(value) {
  return value.replace(/[^A-Za-z]/g, '')
}

const fields = {
  id: {
    label: 'Identificador',
    help: 'Identificador que es fa servir internament.',
    validator: (value) => {
      if (!value) return "L'identificador és requisit"
      if (value.length < 3) return 'Identificador massa curt'
      if (!value.match(/^[a-z]{3,10}$/))
        return "L'identificador nomes pot tenir lletres minuscules"
      return false
    },
    inputFilter: inputFilter_ID,
  },
  name: {
    label: 'Nom mostrat',
    help: 'Nom amb espais, accents, majúscules i el que calgui.',
  },
  email: {
    label: 'Adreça de correu',
    help: 'Correu oficial que tens a Som Energia.',
    validator: (value) => {
      if (value === undefined) return false
      if (value === '') return false
      if (!value.includes('@')) return 'Ha de ser una adreça de correu vàlida'
      return false
    },
  },
  erpuser: {
    label: 'Usuari ERP',
    help: "Usuari amb el que entres a l'erp.",
    validator: (value) => {
      if (value === undefined) return false
      if (value.length === 0) return false
      if (!value.match(/^[a-zA-Z]{3,10}$/))
        return "El nom d'usuari ERP és invàlid"
      return false
    },
    inputFilter: inputFilter_erpuser,
  },
  idealload: {
    label: 'Càrrega de torns',
    help: 'Torns que farà normalment en una setmana de 5 dies laborals. En blanc si no fa atenció.',
    validator: (value) => {
      if (value === undefined) return false // Ok no turns
      if (value === '') return false // Ok no turns
      if (isNaN(parseInt(value))) return 'Ha de ser un número'
      if (parseInt(value) < 0) return 'Ha de ser un número positiu'
      if (parseInt(value) > 10) return 'Ningú pot fer més de 10 torns setmanals'
      return false // Ok a valid number
    },
  },
  extension: {
    label: 'Extensió',
    help: 'Extensió de telèfon assignada a la centraleta.',
    inputFilter: inputFilter_onlyDigits,
  },
  table: {
    label: 'Taula',
    help: 'Posem a la gent propera a la mateixa taula per evitar torns amb cacofonies',
    default: -1,
  },
  color: {
    label: 'Color',
    help: 'Color personal',
    default: 'aaaaff',
  },
  groups: {
    label: 'Groups',
    help: 'Grups als que pertany la persona',
    default: [],
  },
}

const defaultData = Object.fromEntries(
  Object.keys(fields).map((field) => {
    return [field, fields[field]?.default ?? '']
  }),
)


export default function PersonEditor(props) {
  const { open, onClose, onSave, person, tables, allGroups } = props
  const [data, setData] = React.useState(defaultData)
  const [errors, setErrors] = React.useState(() =>
    Object.fromEntries(Object.keys(fields).map(k=>[k, false]))
  )

  // Sets the errors for new data
  function resetData(person) {
    const newData = {
      ...defaultData,
      ...(person || {}),
    }
    setData(newData)
    setErrors({
      ...errors,
      ...Object.fromEntries(
        Object.keys(fields).map((key) => {
          const validator = fields[key].validator
          if (!validator) return [key, false]
          return [key, validator(newData[key])]
        }),
      ),
    })
  }

  React.useEffect(() => {
    resetData(person)
  }, [person])

  function updater(field) {
    return (ev) => {
      const newvalue = ev.target.value
      const validator = fields[field]?.validator
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
      helperText:
        typeof errors[field] === 'string' ? errors[field] : fields[field].help,
      error: !!errors[field],
      value: data[field] === undefined ? defaultData[field] : data[field],
      onChange: updater(field),
      onInput: fields[field].inputFilter !== undefined ? (ev) =>
        fields[field].inputFilter(ev.target.value) : undefined
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
          inputProps={{ pattern: '^[a-zA-Z]{3,10}$' }}
        />
        <TextField
          {...fieldOptions('idealload')}
          {...commonFieldOptions}
          inputProps={{ pattern: '^[0-9]{0,2}$' }}
        />
        <TextField
          {...fieldOptions('extension')}
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
          value={data.groups ?? fields['groups'].default}
          onChange={(ev, newvalue) => setData({ ...data, groups: newvalue })}
          renderInput={(params) => (
            <TextField {...params} label={fields['groups'].label} {...commonFieldOptions} />
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
