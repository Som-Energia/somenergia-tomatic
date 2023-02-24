import React from 'react'
import './App.css'
import TableEditor from './components/TableEditor.js'
import AppFrame from './containers/AppFrame.js'

function App() {
  return (
    <AppFrame>
      <TableEditor />
    </AppFrame>
  )
}

export default App
