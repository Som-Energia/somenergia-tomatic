// KumatoProvider
//
// Provides light and dark themes to the inner components
// based on Tomatic Kumato state.

import React from 'react'
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

export default function KumatoProvider({ children }) {
  const isKumatoMode = Tomatic.isKumatoMode.use()
  return (
    <ThemeProvider theme={isKumatoMode ? darkTheme : ligthTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  )
}
