// KumatoProvider
//
// Provides light and dark themes to the inner components
// based on Tomatic Kumato state.

import * as React from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Tomatic from '../services/tomatic'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
})

const ligthTheme = createTheme({
  palette: {},
})

var updateMode = null
Tomatic.onKumatoChanged.push(() => updateMode && updateMode())

export default function KumatoProvider({ children }) {
  const [isKumatoMode, setKumato] = React.useState(Tomatic.isKumatoMode())
  updateMode = () => {
    setKumato(Tomatic.isKumatoMode())
  }
  return (
    <ThemeProvider theme={isKumatoMode ? darkTheme : ligthTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  )
}
