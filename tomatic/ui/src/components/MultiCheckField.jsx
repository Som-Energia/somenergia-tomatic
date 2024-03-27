import React from 'react'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import Stack from '@mui/material/Stack'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
import FormHelperText from '@mui/material/FormHelperText'

/// Form field represented as a set of checkboxes.
export default function MultiCheckField({
  name,
  variant = 'outlined',
  row = true,
  value,
  onChange,
  options,
  helperText,
  label,
}) {
  const id = React.useId()
  if (!name) name = id
  return (
    <FormControl variant={variant}>
      <FormLabel id={name + '-label'} variant={variant}>
        {label}
      </FormLabel>
      <Stack direction={row ? 'row' : 'column'}>
        {options.map(function (option, i) {
          return (
            <FormControlLabel
              key={i}
              label={option.label}
              control={<Checkbox />}
              checked={!!value[i]}
              onChange={(ev) => onChange(i, ev.target.checked)}
            />
          )
        })}
      </Stack>
      <FormHelperText id={name + '-helper'}>{helperText}</FormHelperText>
    </FormControl>
  )
}
