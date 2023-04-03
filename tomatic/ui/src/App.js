import * as React from 'react'
import './App.css'
import PersonsTable from './components/PersonsTable.js'
import AppFrame from './containers/AppFrame.js'
import Tomatic from './services/tomatic'
import { AuthProvider } from './contexts/AuthContext'
import KumatoProvider from './containers/KumatoProvider'
import { createHashRouter, RouterProvider } from 'react-router-dom'
import MithrilWrapper from './containers/MithrilWrapper'
import customStyle from './mithril/style.styl'
import TimeTablePage from './mithril/components/timetablepage'
import QueueMonitor from './mithril/components/queuemonitor'
import {
  MithrilCallinfoPage,
  MithrilTimeTablePage,
  MithrilQueueMonitor,
} from './components/MithrilPages'

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
      path: '/Persones',
      element: (
        <AppFrame>
          <PersonsTable />
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
    <AuthProvider>
      <KumatoProvider>
        <RouterProvider router={router} />
      </KumatoProvider>
    </AuthProvider>
  )
}

export default App
