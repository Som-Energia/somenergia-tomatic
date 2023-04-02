import * as React from 'react'
import './App.css'
import PersonsTable from './components/PersonsTable.js'
import AppFrame from './containers/AppFrame.js'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Tomatic from './services/tomatic'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
})

const ligthTheme = createTheme({
  palette: {},
})

// TODO: could be turn into a context
var updateMode = null
Tomatic.onKumatoChanged.push(() => updateMode && updateMode())

function App() {
  const [isKumatoMode, setKumato] = React.useState(Tomatic.isKumatoMode)
  updateMode = () => {
    setKumato(Tomatic.isKumatoMode())
  }
  return (
    <ThemeProvider theme={isKumatoMode ? darkTheme : ligthTheme}>
      <CssBaseline />
      <AppFrame>
        <PersonsTable />
      </AppFrame>
    </ThemeProvider>
  )
}

export default App
