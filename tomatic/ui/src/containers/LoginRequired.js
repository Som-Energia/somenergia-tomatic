// LoginRequired
// An adapter for pages that require login.
// If not logged in, it shows a messages redirecting
// to login page.
import * as React from 'react'
import SimpleCard from '../components/SimpleCard'
import AuthContext from '../contexts/AuthContext'
import Auth from '../services/auth'

export default function LoginRequired({ children }) {
  const auth = React.useContext(AuthContext)
  if (auth?.userid) return children
  return (
    <SimpleCard
      title={'Es requereix identificació'}
      error={Auth.error()}
      content={
        "Cal que us identifiqueu a Can Google amb l'usuari de Som Energia."
      }
      button={'Ves-hi!'}
      action={Auth.authenticate}
    />
  )
}
