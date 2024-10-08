import React from 'react'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import IconButton from '@mui/material/IconButton'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Tooltip from '@mui/material/Tooltip'
import Card from '@mui/material/Card'
import TextField from '@mui/material/TextField'
import BackspaceIcon from '@mui/icons-material/Backspace'
import ReplayCircleFilledIcon from '@mui/icons-material/ReplayCircleFilled'
import CallInfo from '../../contexts/callinfo'
import TypificationChooser from './TypificationChooser'
import AuthContext from '../../contexts/AuthContext'

export default function TypificationDialog({ onClose }) {
  const now = new Date().toISOString()
  const [comment, setComment] = React.useState('')
  const [typification, setTypification] = React.useState([])
  const [bindContract, setBindContract] = React.useState(true)
  const { userid, fullname } = React.useContext(AuthContext)
  const partner = CallInfo.selectedPartner()
  const contract = CallInfo.selectedContract()
  const call_id = CallInfo.currentCall.use()

  const call = CallInfo.callData(call_id)
  const phoneNumber = call?.phone_number || 'Entrada manual'
  const timestamp = call?.call_timestamp || now
  const day = new Date(timestamp).toLocaleDateString()
  const time = new Date(timestamp).toLocaleTimeString()
  const person =
    partner !== null
      ? `${partner.id_soci} - ${partner.dni.replace('ES', '')} - ${
          partner.name
        }`
      : 'Cap persona especificada'
  const contractInfo =
    contract !== null && bindContract
      ? contract.number + ' - ' + contract.cups_adress
      : ' Cap contracte especificat'

  function handleClose() {
    onClose()
  }
  function submit() {
    const baseCall = CallInfo.callData(call_id) || {
      // Manual call from scratch
      call_timestamp: timestamp,
      operator: userid,
      pbx_call_id: phoneNumber.split().join('') + now,
      phone_number: phoneNumber,
    }
    const call = {
      ...baseCall,
      caller_erp_id: partner?.erp_id,
      caller_vat: partner?.dni,
      caller_name: partner?.name,
      contract_erp_id: bindContract ? contract?.erp_id : undefined,
      contract_address: bindContract ? contract?.cups_adress : undefined,
      contract_number: bindContract ? contract?.number : undefined,
      category_ids: typification.map((t) => t.id),
      comments: comment,
    }
    CallInfo.modifyCall(call)
    onClose()
  }
  const isValid = typification.length !== 0

  return (
    <>
      <DialogTitle>{'Tipificant trucada'}</DialogTitle>
      <DialogContent>
        <Stack gap={2} minWidth="45vw">
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
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Box>
                <strong>Referent al contracte:</strong> {contractInfo}
              </Box>
              {contract ? (
                <Box>
                  <Tooltip
                    title={
                      bindContract
                        ? 'Desvincular el contracte'
                        : 'Recuperar el contracte'
                    }
                  >
                    <IconButton
                      size="small"
                      onClick={() => {
                        setBindContract((old) => !old)
                      }}
                    >
                      {bindContract ? (
                        <BackspaceIcon />
                      ) : (
                        <ReplayCircleFilledIcon />
                      )}
                    </IconButton>
                  </Tooltip>
                </Box>
              ) : null}
            </Stack>
            <Box>
              <strong>Atesa per:</strong> {fullname}
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
