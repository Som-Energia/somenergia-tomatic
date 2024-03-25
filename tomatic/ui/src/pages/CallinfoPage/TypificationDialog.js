import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Card from '@mui/material/Card'
import TextField from '@mui/material/TextField'
import CallInfo from '../../contexts/callinfo'
import TypificationChooser from './TypificationChooser'
import { useSubscriptable } from '../../services/subscriptable'
import AuthContext from '../../contexts/AuthContext'

export default function TypificationDialog({ onClose }) {
  const [comment, setComment] = React.useState('')
  const [typification, setTypification] = React.useState([])
  const { userid, fullname } = React.useContext(AuthContext)
  const partner = CallInfo.selectedPartner()
  const contract = CallInfo.selectedContract()
  const phoneNumber = CallInfo.call.phone || 'Entrada manual'
  const timestamp =
    CallInfo.call.date === '' ? new Date().toISOString() : CallInfo.call.date
  const day = new Date(timestamp).toLocaleDateString()
  const time = new Date(timestamp).toLocaleTimeString()
  const person =
    partner !== null
      ? `${partner.id_soci} - ${partner.dni.replace('ES', '')} - ${
          partner.name
        }`
      : 'Cap persona especificada'
  const contractInfo =
    contract !== null
      ? contract.number + ' - ' + contract.cups_adress
      : ' Cap contracte especificat'

  function handleClose() {
    onClose()
  }
  function submit() {
    // TODO: actually submit
    console.log('Emulating submission:', {
      user: userid,
      partner: partner?.dni,
      contract: contract?.number,
      calldate: timestamp,
      callphone: phoneNumber,
      typification: typification.map((t) => t.key),
      comment: comment,
    })
    onClose()
  }
  const isValid = !!comment && typification.length !== 0

  return (
    <>
      <DialogTitle>{'Tipificant trucada'}</DialogTitle>
      <DialogContent>
        <Stack gap={2}>
          <Card
            className="final-motius"
            sx={{
              p: 1,
            }}
          >
            <Box>
              <strong>Trucada:</strong> {phoneNumber} <strong>el dia</strong>{' '}
              {day} <strong>a les</strong> {time}
            </Box>
            <Box>
              <strong>De:</strong> {person}
            </Box>
            <Box>
              <strong>Referent al contracte:</strong> {contractInfo}
            </Box>
            <Box>
              <strong>Atésa per:</strong> {fullname}
            </Box>
          </Card>
          <TypificationChooser {...{ typification, setTypification }} />
          <TextField
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            label={'Comentaris'}
            multiline
            variant="standard"
            fullWidth
            rows={4}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>{'Cancel·la'}</Button>
        <Button variant="contained" disabled={!isValid} onClick={submit}>
          {'Envia tipificacíó'}
        </Button>
      </DialogActions>
    </>
  )
}
