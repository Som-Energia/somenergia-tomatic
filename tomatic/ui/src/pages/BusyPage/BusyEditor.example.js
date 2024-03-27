import React from 'react'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import Button from '@mui/material/Button'
import BusyEditor from './BusyEditor'
import { TomaticBusyEditor } from './BusyEditor'
import BusyDialog from './BusyDialog'

export default function Example() {
  const [data, setData] = React.useState({ oneshot: [], weekly: [] })
  const [dialogPerson, setDialogPerson] = React.useState(null)
  return (
    <Container>
      <Paper>
        <h6>Local data BusyEditor</h6>
        <BusyEditor name={'mengano'} {...{ data, setData }} />
        <pre>{JSON.stringify(data, true, ' ')}</pre>
        <Button
          onClick={() => {
            setData(data ? null : { oneshot: [], weekly: [] })
          }}
        >
          {'Emulate loading'}
        </Button>
      </Paper>
      <Paper>
        <h6>API based BusyEditor</h6>
        <TomaticBusyEditor person="david" />
      </Paper>
      <Paper>
        <h6>API based BusyDialog</h6>
        <Button variant="contained" onClick={() => setDialogPerson('david')}>
          Open as dialog
        </Button>
        <BusyDialog person={dialogPerson} setPerson={setDialogPerson} />
      </Paper>
    </Container>
  )
}
