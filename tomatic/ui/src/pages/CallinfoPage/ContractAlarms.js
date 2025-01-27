import React from 'react'
import Card from '@mui/material/Card'
import Box from '@mui/material/Box'

export default function ContractAlarms({ contract }) {
  const alarms = [
    [contract.selfconsumption, 'label-selfconsumption', 'Autoconsum.'],
    [contract.generation, 'label-generation', 'Rep Generation.'],
    [contract.energetica, 'label-energetica', "És d'EnergÈtica."],
    [contract.suspended_invoicing, 'label-alert', 'Facturació suspesa.'],
    [contract.has_debt, 'label-alert', 'Té deute: ' + contract.has_debt],
    [contract.without_binding_partner, 'label-alert', "Origin vinculat al CT sense sòcia."],
  ].filter(([active, className, message]) => active)

  if (alarms.length === 0) {
    return <Card className="extra-info">{'No hi ha informació extra.'}</Card>
  }
  return (
    <Card className="extra-info">
      {alarms.map(([active, className, message]) => (
        <Box key={className} className={className}>
          {message}
        </Box>
      ))}
    </Card>
  )
}
