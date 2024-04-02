import React from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import api from '../../services/api'
import messages from '../../services/messages'
import LaunchDialog from './LaunchDialog'

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
  console.log({ task })
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

  function taskCommand(command, context) {
    api
      .request({
        context,
        url: `/api/planner/api/${command}/${task.name}`,
      })
      .then((result) => {
        console.log({ result })
        updateExecutions()
        messages.success('ok', { context })
      })
  }
  const actions = [
    [isRunning, 'Mata', 'kill', 'Matant la graela'],
    [isRunning, 'Para', 'stop', 'Parant la graela'],
    [isStopped, 'Esborra', 'remove', 'Esborrant la graela'],
    [isComplete, 'Publica', 'upload', 'Puja la graella'],
  ]
  return (
    <>
      <tr>
        <td>{startTime}</td>
        <td>
          <a href={`/api/planner/status/${task.name}`} target="_blank">{task.name}</a>
        </td>
        <td>{task.state}</td>
        <td>
          <a href={`/api/planner/solution/${task.name}`} target="_blank">
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
          {actions.map(([isEnabled, label, command, context]) => {
            if (!isEnabled) return
            return (
              <Button
                onClick={() => taskCommand(command, context)}
                size="small"
              >
                {label}
              </Button>
            )
          })}
        </td>
      </tr>
    </>
  )
}

export default function PlannerPage() {
  const [executions, setExecutions] = React.useState([])
  const [open, setOpen] = React.useState(false)

  function closeLauncher() {
    setOpen(false)
  }
  function updateList() {
    const context = `Obtenint llistat d'execucions de graelles`
    api
      .request({
        context,
        url: '/api/planner/api/list',
      })
      .then((result) => {
        console.log({ result })
        setExecutions(result.tasks)
      })
  }

  React.useEffect(() => {
    updateList()
    const interval = setInterval(() => {
      updateList()
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  return (
    <Box
      sx={{
        '.tooltip': {
          visibility: 'hidden',
          position: 'absolute',
          cursor: 'link',
          width: '20em',
          background: '#ffa',
          border: '1px solid grey',
          padding: '1ex',
        },
        'td:hover .tooltip': { visibility: 'visible' },
      }}
    >
      <LaunchDialog
        open={open}
        onClose={closeLauncher}
        updateExecutions={updateList}
      />
      <Box>
        <a href="/api/planner/clear">Clear</a>
      </Box>
      <Button onClick={() => setOpen(true)}>{'Llença una Graella'}</Button>
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
