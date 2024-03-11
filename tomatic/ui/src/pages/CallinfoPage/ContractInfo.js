import React from 'react'
import Box from '@mui/material/Box'
import CallInfo from '../../mithril/components/callinfo'
import TabbedCard from './TabbedCard'
import { useSubscriptable } from '../../services/subscriptable'

function formatContractNumber(number) {
  var result = number + ''
  while (result.length < 7) result = '0' + result
  return result
}

function formatInterval(contract) {
  var hasStart = contract.start_date !== false
  var hasEnd = contract.end_date !== ''
  if (!hasStart) {
    return 'No especificat'
  }
  if (!hasEnd) {
    return contract.start_date + ' ⇨ Actualitat'
  }
  return contract.start_date + ' ⇨ ' + contract.end_date
}

function InfoLine({ ...rest }) {
  return <Box className="contract-info-item" {...rest} />
}

function Info() {
  const contract = useSubscriptable(CallInfo.selectedContract)
  const s_num = formatContractNumber(contract.number)
  const from_til = formatInterval(contract)
  const roles = [
    ['T', contract.is_titular, 'Titular: Si té el contracte al seu nom'],
    [
      'A',
      contract.is_administrator,
      'Administradora: Si té permís de la titular per veure o gestionar-ho',
    ],
    ['S', contract.is_partner, 'Socia: Si és la socia vinculada al contracte'],
    [
      'P',
      contract.is_payer,
      "Pagadora: Si les factures s'emeten i cobren al seu nom (Rol a extingir)",
    ],
    ['N', contract.is_notifier, 'Notificada: Si en rep notificacions'],
  ]
  return (
    <Box className="contract-info-box">
      <InfoLine>
        <Box>
          <Box className="label-right">{from_til}</Box>
        </Box>
        <Box>
          <Box className="label">{'Número: '}</Box>
          {s_num}
        </Box>
      </InfoLine>
      <InfoLine>
        <Box className="label">{'Nom del titular: '}</Box>
        {contract.titular_name}
      </InfoLine>
      {contract.administrator ? (
        <InfoLine>
          <Box className="label">{'Administradora: '}</Box>
          {contract.administrator}
        </InfoLine>
      ) : null}
      <InfoLine>
        <Box className="label">{'CUPS: '}</Box>
        {contract.cups}
      </InfoLine>
      <InfoLine>
        <Box className="label">{'Adreça CUPS: '}</Box>
        {contract.cups_adress}
      </InfoLine>
      <InfoLine>
        <Box className="label">{'Tarifa: '}</Box>
        {contract.fare}
      </InfoLine>
      <InfoLine>
        {Object.keys(contract.power).map(function (key, index) {
          return (
            <Box>
              <Box className="label">{`${key}: `}</Box>
              {contract.power[key] + ' kW'}
            </Box>
          )
        })}
      </InfoLine>
      <InfoLine>
        <Box className="label">{'IBAN: '}</Box>
        {contract.iban}
      </InfoLine>
      <InfoLine>
        <Box className="label-right">
          {'Rols: '}
          {roles.map(function (rol) {
            var letter = rol[0]
            var active = rol[1]
            var title = rol[2]
            return (
              <Box
                className={'contract-role' + (active ? ' active' : '')}
                title={title}
              >
                {letter}
              </Box>
            )
          })}
        </Box>
      </InfoLine>
      <InfoLine>
        <Box className="label">{'Estat pendent: '}</Box>
        {contract.pending_state ? contract.pending_state : 'Esborrany'}
      </InfoLine>
      <br />
      {
        [
          //TODO extraInfo(contract),
        ]
      }
    </Box>
  )
}

function NoContracts() {
  return (
    <Box className="contracts">
      <Box className="no-info">{'No hi ha contractes.'}</Box>
    </Box>
  )
}

export default function ContractInfo(
  data,
  currentPartner,
  setCurrentPartner,
  currentContract,
  setCurrentContract,
) {
  const partner = useSubscriptable(CallInfo.selectedPartner)
  const contract = useSubscriptable(CallInfo.selectedContract)
  if (contract === null) {
    return <NoContracts />
  }
  const contracts = partner.contracts
  function onTabChanged(value) {
    setCurrentContract && setCurrentContract(value)
    CallInfo.selectContract(value)
    CallInfo.notifyUsage('callinfoChangeContract')
  }
  return (
    <Box className="contracts">
      <TabbedCard
        currentTab={CallInfo.currentContract}
        onTabChanged={onTabChanged}
        labels={contracts.map((contract) => (
          <span className={contract.end_date ? 'inactive-contract' : ''}>
            {contract.number}
          </span>
        ))}
        Inner={Info}
      />
    </Box>
  )
}
