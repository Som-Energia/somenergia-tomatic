import React from 'react'
import TextField from '@mui/material/TextField'
import Autocomplete from '@mui/material/Autocomplete'

// TODO: use category from api
const categories = [
  {
    label: 'Serveis de Comercialització - Estat instal·lacions',
    key: 'comer:instal',
  },
  {
    label: 'Serveis de Comercialització - Facturacio - Transversal',
    key: 'comer:factura-transversal',
  },
  {
    label: 'Serveis de Comercialització - Facturacio - Generation kWh',
    key: 'comer:factura:generation',
  },
  {
    label: 'Serveis de Comercialització - Facturacio - Auto',
    key: 'comer:factura:auto',
  },
  {
    label: 'Serveis de Comercialització - Facturacio - Grans Consums',
    key: 'comer:factura:grans',
  },
  {
    label: 'Serveis de Comercialització - Cobraments - Modificació',
    key: 'comer:cobraments:modificacions',
  },
  {
    label: 'Serveis de Comercialització - Cobraments - Procediment',
    key: 'comer:cobraments:procediments',
  },
]

export default function TypificationChooser({ typification, setTypification }) {
  return (
    <Autocomplete
      multiple
      options={categories}
      filterSelectedOptions
      value={typification}
      onChange={(ev, value) => {
        console.log({ value })
        setTypification(value)
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
