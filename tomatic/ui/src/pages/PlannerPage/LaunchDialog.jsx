import React from 'react'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Autocomplete from '@mui/material/Autocomplete'
import Button from '@mui/material/Button'
import Dialog from '../../components/ResponsiveDialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import planner from './planner'

function nextMonday() {
  // TODO: Review and test
  const day = new Date()
  day.setDate(day.getDate() + 7 - day.getDay() + 1)
  return day.toISOString().slice(0, 10)
}
const searchDaysOptions = 'dl dm dx dj dv'.split(' ')

export default function LaunchDialog({ open, onClose, updateExecutions }) {
  const [nLines, setNLines] = React.useState(8)
  const [description, setDescription] = React.useState('')
  const [searchDays, setSearchDays] = React.useState([])
  const [monday, setMonday] = React.useState(nextMonday())

  function launchTask() {
    const params = {
      nlines: nLines,
      search_days: searchDays.join(','),
      description,
      monday,
    }
    planner.launch(params).then((result) => {
      updateExecutions()
    })
    onClose()
  }
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{'Llença la graella'}</DialogTitle>
      <DialogContent>
        <Stack mt={2} gap={2} span={1} flex={2}>
          <TextField
            label={'Setmana'}
            name="monday"
            type="date"
            value={monday}
            onChange={(ev) => setMonday(ev.target.value)}
            step={7}
            required
          />
          <TextField
            label={'Linies'}
            name="nLines"
            type="number"
            value={nLines}
            onChange={(ev) => setNLines(ev.target.value)}
            step={1}
            required
          />
          <TextField
            label="Descripció"
            name="description"
            value={description}
            onChange={(ev) => setDescription(ev.target.value)}
            helperText={'Per identificar la tasca a la llista de sota.'}
          />
          <Autocomplete
            multiple
            options={searchDaysOptions}
            filterSelectedOptions
            value={searchDays}
            onChange={(ev, value) => {
              setSearchDays(value)
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Dies a omplir primer"
                name="search_days"
                type="text"
                helperText={
                  'Sovint desencallem la graella posant primer els dies més complicats'
                }
              />
            )}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button variant="outlined" onClick={launchTask}>
          {'Llençar'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
