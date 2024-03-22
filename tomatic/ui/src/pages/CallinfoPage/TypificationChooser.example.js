import React from 'react'
import TypificationChooser from './TypificationChooser'
import Container from '@mui/material/Container'

export default function Example() {
  const [typification, setTypification] = React.useState([])
  return (
    <Container>
      <TypificationChooser {...{ typification, setTypification }} />
    </Container>
  )
}
