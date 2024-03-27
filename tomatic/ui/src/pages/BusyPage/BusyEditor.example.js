import React from 'react'
import Container from '@mui/material/Container'
import BusyEditor from './BusyEditor'

export default function Example() {
  const [data, setData] = React.useState({ oneshot: [], weekly: [] })
  return (
    <Container>
      <BusyEditor name={'mengano'} {...{ data, setData }} />
      <pre>{JSON.stringify(data, true, ' ')}</pre>
    </Container>
  )
}
