import * as React from 'react'
import './App.css'
import AppFrame from './containers/AppFrame.js'
import Tomatic from './services/tomatic'
import { AuthProvider } from './contexts/AuthContext'
import KumatoProvider from './containers/KumatoProvider'
import { createHashRouter, RouterProvider, Outlet } from 'react-router-dom'
import PersonsTable from './components/PersonsTable.js'
import TimeTablePage from './components/TimeTablePage'
import DialogProvider from './components/DialogProvider'
import ComponentTestPage from './pages/ComponentTestPage'
import CallinfoPage from './pages/CallinfoPage'
import BusyPage from './pages/BusyPage'
import PbxPage from './pages/PbxPage'

import {
  MithrilQueueMonitor,
  MithrilPersonsPage,
} from './components/MithrilPages'
import ForcedTurns from './components/ForcedTurns'

Tomatic.init()

function Frame() {
  return <AppFrame>
    <Outlet />
  </AppFrame>
}

const router = createHashRouter(
  [
    {
      path: '/',
      Component: Frame,
      children: [
        {
          path: '/',
          Component: TimeTablePage,
        },
        {
          path: 'Test',
          Component: ComponentTestPage,
        },
        {
          path: 'Administration',
          Component: PersonsTable,
        },
        {
          path: 'ForcedTurns',
          Component: ForcedTurns,
        },
        {
          path: 'Indisponibilitats/:person',
          Component: BusyPage,
        },
        {
          path: 'Persones',
          Component: MithrilPersonsPage,
        },
        {
          path: 'Graelles',
          Component: TimeTablePage,
        },
        {
          path: 'Centraleta/Old',
          Component: MithrilQueueMonitor,
        },
        {
          path: 'Centraleta',
          Component: PbxPage,
        },
        {
          path: 'Trucada',
          Component: CallinfoPage,
        },
      ],
    },
  ],
  {
    //basename: '/admin.html',
  },
)

function App() {
  return (
    <div id="tomatic" className="main">
      <AuthProvider>
        <KumatoProvider>
          <DialogProvider>
            <RouterProvider router={router} />
          </DialogProvider>
        </KumatoProvider>
      </AuthProvider>
    </div>
  )
}

export default App
