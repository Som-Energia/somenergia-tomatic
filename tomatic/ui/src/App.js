import * as React from 'react'
import './App.css'
import PersonsTable from './components/PersonsTable.js'
import AppFrame from './containers/AppFrame.js'
import Tomatic from './services/tomatic'
import { AuthProvider } from './contexts/AuthContext'
import KumatoProvider from './containers/KumatoProvider'

function App() {
  return (
    <AuthProvider>
      <KumatoProvider>
        <AppFrame>
          <PersonsTable />
        </AppFrame>
      </KumatoProvider>
    </AuthProvider>
  )
}

export default App
