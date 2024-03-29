import React from 'react'
import Box from '@mui/material/Box'
import IconButton from '@mui/material/IconButton'
import EventBusyIcon from '@mui/icons-material/EventBusy'
import EditIcon from '@mui/icons-material/Edit'
import PersonEditor from '../../components/PersonEditor'
import BusyDialog from '../BusyPage/BusyDialog'
import { useDialog } from '../../components/DialogProvider'
import { useSubscriptable } from '../../services/subscriptable'
import Tomatic from '../../services/tomatic'

export default function Persons() {
  const [openDialog, closeDialog] = useDialog()
  const [personToEditBusy, setPersonToEditBusy] = React.useState()
  const { extensions } = Tomatic.persons.use()
  function editPerson(name) {
    openDialog({
      children: (
        <PersonEditor
          onClose={closeDialog}
          onSave={(id, data) => {
            Tomatic.setPersonDataReact(id, data)
            closeDialog()
          }}
          person={Tomatic.personFields(name)}
          allGroups={Tomatic.allGroups()}
          tables={Tomatic.tableOptions()}
        />
      ),
    })
  }
  function editBusy(name) {
    setPersonToEditBusy(name)
  }
  return (
    <Box className="extensions">
      <BusyDialog person={personToEditBusy} setPerson={setPersonToEditBusy} />
      {Object.keys(extensions || {})
        .sort()
        .map((name) => (
          <Box key={name} className={`extension ${name}`}>
            {Tomatic.formatName(name)}
            <br />
            {extensions[name] || <>&nbsp;</>}
            <Box className="tooltip">
              <IconButton className="colored" onClick={() => editBusy(name)}>
                <EventBusyIcon />
              </IconButton>
              <IconButton className="colored" onClick={() => editPerson(name)}>
                <EditIcon />
              </IconButton>
            </Box>
          </Box>
        ))}
      <Box className={`extension add`} onClick={()=>editPerson()}>
        {'nova'} <br /> {'persona'}
      </Box>
    </Box>
  )
}
