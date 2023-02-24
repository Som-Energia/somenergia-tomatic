import React from 'react'
import TableEditor from './TableEditor'

function PersonsTable() {
  return <TableEditor 
    title={"Persones"}
    defaultPageSize={12}
    pageSizes={[12, 18, 25]}
  />
}

export default PersonsTable

