import * as React from 'react'
import Card from '@mui/material/Card'
import AuthContext from '../contexts/AuthContext'

export default function LoginRequired({ children }) {
  const auth = React.useContext(AuthContext)
  if (auth?.userid) return children
  return <Card>NOOOO</Card>
}
