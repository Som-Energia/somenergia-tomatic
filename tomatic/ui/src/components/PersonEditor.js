import React from 'react'
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
    pattern: '[a-z]{3,10}$',
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
    pattern: '^[a-zA-Z]{3,10}$',
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
    pattern: '^[0-9]{0,2}$',
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
    pattern: '^[0-9]{4}$',
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

const errorReset = Object.fromEntries(
  Object.keys(fields).map((k) => [k, false]),
)

export default function PersonEditor(props) {
  const { onClose, onSave, person, tables, allGroups } = props
  const [data, setData] = React.useState(defaultData)
  const [errors, setErrors] = React.useState(errorReset)

  function updateField(field, value) {
    setData({ ...data, [field]: value })
  }

  // Reset internal data as the person passed by parameter changes
  React.useEffect(() => {
    const newData = {
      ...defaultData,
      ...(person || {}),
    }
    setData(newData)
    setErrors({
      ...errorReset,
      ...Object.fromEntries(
        Object.keys(fields).map((key) => {
          const validator = fields[key].validator
          if (!validator) return [key, false]
          return [key, validator(newData[key])]
        }),
      ),
    })
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
      updateField(field, newvalue)
    }
  }
  const fieldOptions = (field) => {
    const fieldErrors = errors[field]
    const fieldParams = fields[field]
    return {
      id: field,
      label: fieldParams.label,
      helperText:
        typeof fieldErrors === 'string' ? fieldErrors : fieldParams.help,
      error: !!fieldErrors,
      value: data[field] === undefined ? defaultData[field] : data[field],
      onChange: updater(field),
      onInput:
        fieldParams.inputFilter !== undefined
          ? (ev) => fieldParams.inputFilter(ev.target.value)
          : undefined,
      inputProps: fieldParams.pattern
        ? { pattern: fieldParams.pattern }
        : undefined,
    }
  }

  const commonFieldOptions = {
    fullWidth: true,
    variant: 'standard',
    margin: 'dense',
  }

  const isNew = person?.id === undefined

  return (
    <div
      aria-labelledby="person-editor-title"
      aria-describedby="person-editor-description"
    >
      <DialogTitle id="person-editor-title">
        {isNew
          ? 'Afegeix una persona nova'
          : 'Edita la informació de la persona'}
      </DialogTitle>
      <DialogContent>
        <TextField
          disabled={!isNew}
          autoFocus={isNew}
          required
          {...fieldOptions('id')}
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
        <TextField {...fieldOptions('erpuser')} {...commonFieldOptions} />
        <TextField {...fieldOptions('idealload')} {...commonFieldOptions} />
        <TextField {...fieldOptions('extension')} {...commonFieldOptions} />
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
            updateField(field, newvalue)
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
          onChange={(ev, newvalue) => updateField('groups', newvalue)}
          renderInput={(params) => (
            <TextField
              {...params}
              label={fields['groups'].label}
              {...commonFieldOptions}
            />
          )}
        />
      </DialogContent>
      <DialogActions>
        {Object.values(errors).some((x) => x) ? (
          <Alert severity="error">{'Hi ha camps incorrectes'}</Alert>
        ) : (
          // Placeholder
          <Alert severity="success" sx={{ opacity: 0 }}>
            {'Tots els camps son correctes'}
          </Alert>
        )}
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
    </div>
  )
}
