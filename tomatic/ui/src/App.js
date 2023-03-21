import * as React from "react"
import "./App.css"
import PersonsTable from "./components/PersonsTable.js"
import AppFrame from "./containers/AppFrame.js"

function App() {
  return (
    <AppFrame>
      <PersonsTable />
    </AppFrame>
  )
}

export default App
