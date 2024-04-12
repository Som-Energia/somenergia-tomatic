import React from 'react'
import Container from '@mui/material/Container'
import Card from '@mui/material/Card'
import Stack from '@mui/material/Stack'
import { useParams } from 'react-router-dom'
import { TomaticBusyEditor } from './BusyEditor'
import BusyNotes from './BusyNotes'
import Tomatic from '../../services/tomatic'

export default function BusyPage() {
  const { person } = useParams()
  const fullName = Tomatic.formatName(person)
  return (
    <Container sx={{ p: 2 }}>
      <Stack gap={1}>
        <h2
          style={{ textAlign: 'center' }}
        >{`Indisponibilitats - ${fullName}`}</h2>
        <Card>
          <TomaticBusyEditor person={person} />
        </Card>
        <Card>
          <BusyNotes />
        </Card>
      </Stack>
    </Container>
  )
}
