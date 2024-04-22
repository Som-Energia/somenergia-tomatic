import React from 'react'
import TextField from '@mui/material/TextField'
import Autocomplete from '@mui/material/Autocomplete'
import CallInfo from '../../contexts/callinfo'

export default function TypificationChooser({ typification, setTypification }) {
  const categories = CallInfo.categories.use()

  function searchMatches(searchQuery, category) {
    if (!searchQuery) return true
    console.log({ searchQuery, category })
    return searchQuery
      .toLowerCase()
      .split(' ')
      .every((searchWord) => {
        if (category.name.toLowerCase().includes(searchWord)) return true
        return category.keywords.some((kw) =>
          kw.toLowerCase().includes(searchWord),
        )
      })
  }
  function filterCategories(query, categories) {
        const loweredSearch = query.toLowerCase()
        return categories.filter((category) => searchMatches(loweredSearch, category))
  }

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
      filterOptions={(options, state) => {
        const query = state.inputValue
        return filterCategories(query, options)
      }}
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
