import * as React from 'react'
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
import ForcedTurns from './components/ForcedTurns'
import BusyPage from './pages/BusyPage'
import PbxPage from './pages/PbxPage'
import PersonsPage from './pages/PersonsPage'
// TODO: Cleanup styles, some even inherited from polythene
import * as css from 'polythene-css'
import CssBaseline from '@mui/material/CssBaseline'
import PersonStyles from './components/PersonStyles'
import './App.css'
import './containers/style.styl'
css.addLayoutStyles()
css.addTypography()

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
          Component: PersonsPage,
        },
        {
          path: 'Graelles',
          Component: TimeTablePage,
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
      <CssBaseline />
      <PersonStyles />
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
