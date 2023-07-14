import * as React from 'react'
import './App.css'
import AppFrame from './containers/AppFrame.js'
import Tomatic from './services/tomatic'
import { AuthProvider } from './contexts/AuthContext'
import KumatoProvider from './containers/KumatoProvider'
import { createHashRouter, RouterProvider } from 'react-router-dom'
import PersonsTable from './components/PersonsTable.js'

import {
  MithrilCallinfoPage,
  MithrilTimeTablePage,
  MithrilQueueMonitor,
  MithrilPersonsPage,
} from './components/MithrilPages'
import ForcedTurns from './components/ForcedTurns'

Tomatic.init()

const router = createHashRouter(
  [
    {
      path: '/',
      element: (
        <AppFrame>
          <MithrilTimeTablePage />
        </AppFrame>
      ),
    },
    {
      path: '/Administration',
      element: (
        <AppFrame>
          <PersonsTable />
        </AppFrame>
      ),
    },
    {
      path: '/ForcedTurns',
      element: (
        <AppFrame>
          <ForcedTurns/>
        </AppFrame>
      ),
    },
    {
      path: '/Persones',
      element: (
        <AppFrame>
          <MithrilPersonsPage />
        </AppFrame>
      ),
    },
    {
      path: '/Graelles',
      element: (
        <AppFrame>
          <MithrilTimeTablePage />
        </AppFrame>
      ),
    },
    {
      path: '/Centraleta',
      element: (
        <AppFrame>
          <MithrilQueueMonitor />
        </AppFrame>
      ),
    },
    {
      path: '/Trucada',
      element: (
        <AppFrame>
          <MithrilCallinfoPage />
        </AppFrame>
      ),
    },
  ],
  {
    //basename: '/admin.html',
  }
)

function App() {
  return (
    <div id="tomatic" className='main'>
      <AuthProvider>
        <KumatoProvider>
          <RouterProvider router={router} />
        </KumatoProvider>
      </AuthProvider>
    </div>
  )
}

export default App
