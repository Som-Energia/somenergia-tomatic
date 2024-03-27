import React from 'react'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import RadioGroup from '@mui/material/RadioGroup'
import Radio from '@mui/material/Radio'
import FormControlLabel from '@mui/material/FormControlLabel'
import FormHelperText from '@mui/material/FormHelperText'

/// Form field represented as a radio button group.
export default function RadioField({
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
      <RadioGroup
        row={row}
        aria-labelledby={name + '-label'}
        name={name}
        value={value}
        onChange={onChange}
      >
        {options.map((option, i) => (
          <FormControlLabel control={<Radio />} key={i} {...option} />
        ))}
      </RadioGroup>
      <FormHelperText id={name + '-helper'}>{helperText}</FormHelperText>
    </FormControl>
  )
}
