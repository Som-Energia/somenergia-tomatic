import React from 'react'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import CallInfo from '../../contexts/callinfo'
import { useSubscriptable } from '../../services/subscriptable'

export default function Invoices() {
  const isLoading = CallInfo.loadingDetails.use()
  const contract = useSubscriptable(CallInfo.selectedContract)
  const invoices = contract?.invoices ?? null
  if (isLoading) {
    return (
      <Box className="factures">
        <Box className="loading  layout vertical center">
          {'Carregant factures...'}
          <CircularProgress />
        </Box>
      </Box>
    )
  }
  if (invoices.length === 0) {
    return (
      <Box className="factures">
        <Box className="loading  layout vertical center">
          {'No hi ha factures disponibles'}
        </Box>
      </Box>
    )
  }
  return (
    <Box className="factures">
      {invoices.map(function (invoice, i) {
        return (
          <Box className="factura-info-item" key={i}>
            <Box>
              <Box className="label-right">
                {invoice.initial_date + ' ⇨ ' + invoice.final_date}
              </Box>
              <Box>
                <Box className="label">{'Factura'}</Box>
                {invoice.number}
              </Box>
            </Box>
            <Box>
              <Box className="label">{'Empresa'}</Box>
              {invoice.payer}
            </Box>
            <table>
              <thead>
                <tr>
                  <th>{'Total'}</th>
                  <th>{'Energia'}</th>
                  <th>{'Dies'}</th>
                  <th>{'Emissió'}</th>
                  <th>{'Venciment'}</th>
                  <th>{'Estat'}</th>
                </tr>
              </thead>
              <tbody>
                <tr key={i}>
                  <td>{invoice.amount}</td>
                  <td>{invoice.energy_invoiced}</td>
                  <td>{invoice.days_invoiced}</td>
                  <td>{invoice.invoice_date}</td>
                  <td>{invoice.due_date}</td>
                  <td>{invoice.state}</td>
                </tr>
              </tbody>
            </table>
          </Box>
        )
      })}
    </Box>
  )
}
