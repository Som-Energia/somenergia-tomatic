import React from 'react'
import Tomatic from '../services/tomatic'
import Grid from '@mui/material/Grid'
import styled from '@emotion/styled'


function PersonPickerCell({ name, onPick }) {
  const CellItem = styled.div`
    cursor: pointer;
    text-align: center;
    padding: 0.5em;
    width: 10em;
    margin: 0.3em;
    :hover {
      opacity: 70%;
    }
  `
  return (
    <CellItem
      key={name}
      className={'extension ' + name}
      onClick={() => onPick(name)}
    >
      {Tomatic.formatName(name)}
    </CellItem>
  )
}

function PersonPicker(props) {
  const { onPick, nobodyPickable } = props
  var extensions = Tomatic.persons().extensions || {}
  return (
    <Grid
      style={{ width: '100%', margin: 1, justifyContent: 'center' }}
      container
      spacing={{ xs: 4, md: 4 }}
    >
      {Object.keys(extensions)
        .sort()
        .map((name, i) => <PersonPickerCell name={name} key={i} onPick={onPick}/>)}
      {nobodyPickable ? <PersonPickerCell name={'ningu'} onPick={onPick}/> : []}
    </Grid>
  )
}

export default PersonPicker
