import React from 'react'
import Container from '@mui/material/Container'
import Doc from '../../components/Doc'
import QueueMonitor from './QueueMonitor'

export default function PbxPage() {
  return (
    <>
      <Doc
        message={
          'Visualitza les línies que estan actualment rebent trucades. ' +
          "Feu click al damunt per pausar-les o al signe '+' per afegir-ne"
        }
      />
      <Container sx={{ padding: 2 }}>
        <h2 style={{ textAlign: 'center' }}>{'Linies en cua'}</h2>
        <QueueMonitor />
      </Container>
    </>
  )
}
