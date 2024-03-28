import React from 'react'
import Box from '@mui/material/Box'
import Doc from '../../components/Doc'
//import PersonsTable from '../../components/PersonsTable'
import Persons from './/Persons'

export default function PbxPage() {
  return (
    <>
      <Doc
        message={
        'Permet modificar la configuració personal de cadascú: ' +
          'Color, taula, extensió, indisponibilitats...'
        }
      />
      <Box sx={{padding: 2}}>
        <Persons />
      </Box>
    </>
  )
}

