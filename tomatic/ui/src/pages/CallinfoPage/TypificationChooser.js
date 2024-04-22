import React from 'react'
import TextField from '@mui/material/TextField'
import Autocomplete from '@mui/material/Autocomplete'
import CallInfo from '../../contexts/callinfo'

export default function TypificationChooser({ typification, setTypification }) {
  const categories = CallInfo.categories.use()
  return (
    <Autocomplete
      multiple
      options={categories}
      filterSelectedOptions
      value={typification}
      onChange={(ev, value) => {
        setTypification(value)
      }}
      getOptionLabel={(x) => x.name}
      getOptionDisabled={(x) => !x.enabled}
      getOptionKey={(x) => x.code}
      noOptionsText={'Cap categoria coincideix'}
      renderInput={(params) => (
        <TextField
          {...params}
          label={'Tipificació'}
          variant="standard"
          fullWidth
          helperText={'Desplega per veure les opcions o escriu per filtrar-les'}
        />
      )}
    />
  )
}
