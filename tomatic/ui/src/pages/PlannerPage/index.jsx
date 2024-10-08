import React from 'react'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Button from '@mui/material/Button'
import planner from './planner'
import LaunchDialog from './LaunchDialog'
import SkateboardingIcon from '@mui/icons-material/Skateboarding'
import DeleteIcon from '@mui/icons-material/Delete'
import PublishIcon from '@mui/icons-material/Publish'
import StopIcon from '@mui/icons-material/StopCircle'
import KillIcon from '@mui/icons-material/Dangerous'

const refreshSeconds = 2

function humanDuration(milliseconds) {
  const seconds = Math.floor(milliseconds / 1000)
  if (seconds < 1) return 'res'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 1) return `${seconds % 60} s`
  const hours = Math.floor(minutes / 60)
  if (hours < 1 || true) return `${minutes % 60} m ${seconds % 60} s`
  const days = Math.floor(minutes / 24)
  if (days < 1 || true) return `${hours % 24} h ${minutes % 60} m`
  return `${days} dies ${hours % 24} h`
}

function BusyReasons({ task }) {
  if (!task.busyReasons.length) return
  return (
    <div className="tooltip">
      <h6>Indisponibilitats de {task.unfilledCell}</h6>
      {Object.entries(task.busyReasons).map(([name, reasons]) => {
        return reasons.map((reason, i) => (
          <React.Fragment key={i}>
            <b>{name}</b> {reason}
            <br />
          </React.Fragment>
        ))
      })}
    </div>
  )
}

function Penalties({ task }) {
  if (!task.penalties) return
  return (
    <div className="tooltip">
      <h6>Penalitzacions</h6>
      {task.penalties.map(([penalty, reason], i) => {
        return (
          <React.Fragment key={i}>
            <b>{penalty}</b> {reason}
            <br />
          </React.Fragment>
        )
      })}
    </div>
  )
}

function TaskInfo({ task, updateExecutions }) {
  const isRunning = task.state === 'Running'
  const isStopped = task.state === 'Stopped'
  const isComplete =
    task.completedCells && task.completedCells === task.totalCells
  const now = new Date()
  const startTime = task.startTime.toISOString()
  const timeSinceLastSolution = task.timeOfLastSolution
    ? `fa ${humanDuration(now - task.timeOfLastSolution)}`
    : '--'
  const completedCells = task.completedCells || '--'
  const totalCells = task.totalCells || '--'
  const solutionCost = task.solutionCost || '--'
  const unfilledCell = task.unfilledCell || '??'

  const actions = [
    [isRunning, 'Para', planner.stop, StopIcon],
    [isRunning, 'Mata', planner.kill, KillIcon],
    [isStopped, 'Esborra', planner.remove, DeleteIcon],
    [isComplete, 'Publica', planner.upload, PublishIcon],
  ]
  function runTaskCommand(command) {
    command(task).then((result) => updateExecutions())
  }
  return (
    <tr key={task.name}>
      <td>{startTime}</td>
      <td>
        <a
          href={`/api/planner/status/${task.name}`}
          rel="noreferrer"
          target="_blank"
        >
          {task.name}
        </a>
      </td>
      <td>{task.state}</td>
      <td>
        <a
          href={`/api/planner/solution/${task.name}`}
          rel="noreferrer"
          target="_blank"
        >
          {completedCells}/{totalCells}
        </a>
      </td>
      <td>
        {unfilledCell} <BusyReasons task={task} />
      </td>
      <td>
        {solutionCost} <Penalties task={task} />
      </td>
      <td>{timeSinceLastSolution}</td>
      <td>
        {actions.map(([isEnabled, label, command, Icon]) => {
          if (!isEnabled) return null
          return (
            <Button
              startIcon={<Icon />}
              onClick={() => runTaskCommand(command)}
              size="small"
              key={command}
            >
              {label}
            </Button>
          )
        })}
      </td>
    </tr>
  )
}

export default function PlannerPage() {
  const [executions, setExecutions] = React.useState([])
  const [open, setOpen] = React.useState(false)

  function closeLauncher() {
    setOpen(false)
  }
  function updateList() {
    planner.list().then(setExecutions)
  }

  React.useEffect(() => {
    updateList()
    const interval = setInterval(() => {
      updateList()
    }, refreshSeconds * 1000)

    return () => clearInterval(interval)
  }, [])

  return (
    <Box
      sx={{
        '.tooltip': {
          visibility: 'hidden',
          position: 'absolute',
          cursor: 'text',
          width: '20em',
          background: '#ffa',
          color: 'black',
          border: '1px solid #aaa',
          padding: '1ex',
          zIndex: 1000,
        },
        '.tooltip h6': {
          m: 0,
          mb: 2,
          p: 0,
        },
        'td:hover .tooltip': { visibility: 'visible' },
        'tbody tr:hover': { backgroundColor: '#7771' },
      }}
    >
      <Stack
        direction="row"
        justifyContent="end"
        alignItems="center"
        margin={1}
      >
        <h2>Planificador de graelles</h2>
        <Box flex={1} />
        <Box>
          <Button
            variant="contained"
            onClick={() => setOpen(true)}
            startIcon={<SkateboardingIcon />}
          >
            {'Petri-llença una Graella'}
          </Button>
          <LaunchDialog
            open={open}
            onClose={closeLauncher}
            updateExecutions={updateList}
          />
        </Box>
      </Stack>
      <table width="100%">
        <thead>
          <tr>
            <th>Start time</th>
            <th>Name</th>
            <th>State</th>
            <th>Completion</th>
            <th>Celda bloqueo</th>
            <th>Cost</th>
            <th>Darrera bona</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {executions.map((task, i) => (
            <TaskInfo task={task} key={i} updateExecutions={updateList} />
          ))}
        </tbody>
      </table>
    </Box>
  )
}
