import React from 'react'
import Tomatic from '../services/tomatic'
import Grid from '@mui/material/Grid'
import styled from '@emotion/styled'

function PersonPicker(props) {
  const { onPick, nobodyPickable } = props

  var extensions = Tomatic.persons().extensions || {}

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
  const CellItemNingu = styled.div`
    cursor: pointer;
    text-align: center;
    padding: 0.5em 1em 0.5em 1em;
    width: 10em;
    margin: 0.3em;
    :hover {
      opacity: 70%;
    }
  `

  function pickCell(name) {
    if (name === 'ningu') {
      return (
        <CellItemNingu
          className={'extension ' + name}
          onClick={() => onPick(name)}
        >
          {Tomatic.formatName(name)}
        </CellItemNingu>
      )
    }
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
  return (
    <Grid
      style={{ width: '100%', margin: 1, justifyContent: 'center' }}
      container
      spacing={{ xs: 4, md: 4 }}
    >
      {Object.keys(extensions)
        .sort()
        .map((name) => pickCell(name))}
      {nobodyPickable ? pickCell('ningu') : []}
    </Grid>
  )
}

export default PersonPicker
