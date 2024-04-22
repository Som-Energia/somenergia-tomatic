import React from 'react'
import Chip from '@mui/material/Chip'
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
      renderOption={(props, option, state, ownerSate) => (
        <Box
          element={<li />}
          {...props}
          sx={{
            ...props.sx,
            bgcolor: option.color,
            color: (theme) =>
              option.color && theme.palette.getContrastText(option.color),
            ':hover': {
              color: 'inherit',
            },
          }}
        >
          {option.name}
        </Box>
      )}
      renderTags={(value, getTagProps) =>
        // Only for the color
        value.map((option, index) => (
          <Chip
            sx={{
              bgcolor: option.color,
              color: (theme) =>
                option.color && theme.palette.getContrastText(option.color),
              '.MuiChip-deleteIcon': {
                color: (theme) =>
                  option.color && theme.palette.getContrastText(option.color),
                opacity: 0.9,
              },
              '.MuiChip-deleteIcon': {
                color: (theme) =>
                  option.color && theme.palette.getContrastText(option.color),
                opacity: 0.9,
              },
            }}
            label={option.name}
            {...getTagProps({ index })}
          />
        ))
      }
    />
  )
}
