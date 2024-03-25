import React from 'react'
import TextField from '@mui/material/TextField'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import MenuItem from '@mui/material/MenuItem'
import CallInfo from '../../contexts/callinfo'
import autofiltertype from '../../services/autofiltertype'
import { useSubscriptable } from '../../services/subscriptable'

function TypeOfSearch({ fieldguess }) {
  const { field } = useSubscriptable(CallInfo.search_query)
  const fields = {
    phone: 'Telèfon',
    name: 'Cognoms/Nom',
    nif: 'NIF',
    soci: 'Número Soci',
    email: 'Email',
    contract: 'Contracte',
    cups: 'CUPS',
    all: 'Tot',
  }
  const options = Object.assign(
    { auto: 'Auto' + (fieldguess ? ` (${fields[fieldguess]})` : '') },
    fields,
  )
  return (
    <TextField
      className="select-search flex"
      label="Criteri"
      select
      size="small"
      variant="standard"
      fullWidth
      onChange={function (ev) {
        CallInfo.search_query({ field: ev.target.value })
      }}
      value={field}
    >
      {Object.keys(options).map((key, i) => {
        return (
          <MenuItem value={key} key={i + ''}>
            {options[key]}
          </MenuItem>
        )
      })}
      >
    </TextField>
  )
}

export default function CustomerSearch() {
  const { text } = useSubscriptable(CallInfo.search_query)
  const fieldGuess = autofiltertype(text.trim())
  function handleSearch() {
    CallInfo.searchCustomer()
  }
  return (
    <div className="busca-info">
      <div className="busca-info-title layout horizontal">
        <TypeOfSearch fieldguess={fieldGuess} />
        <TextField
          className="search-query flex"
          fullWidth
          variant="standard"
          label={'Cercador'}
          value={text}
          onChange={(ev) => CallInfo.search_query({ text: ev.target.value })}
          onKeyDown={(ev) => {
            if (ev.key === 'Enter') handleSearch()
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="Submit Search"
                  onClick={handleSearch}
                  variant="standard"
                >
                  <div className="icon-search">
                    <i className="fas fa-search" />
                  </div>
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </div>
    </div>
  )
}
// vim: ts=2 sw=2 et
