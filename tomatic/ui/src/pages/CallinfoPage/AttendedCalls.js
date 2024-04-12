import React from 'react'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Card from '@mui/material/Card'
import CardHeader from '@mui/material/CardHeader'
import CardContent from '@mui/material/CardContent'
import List from '@mui/material/List'
import ListSubheader from '@mui/material/ListSubheader'
import ListItem from '@mui/material/ListItem'
import ListItemText from '@mui/material/ListItemText'
import IconButton from '@mui/material/IconButton'
import CircularProgress from '@mui/material/CircularProgress'
import CallInfo from '../../contexts/callinfo'
import Auth from '../../services/auth'
import { useDialog } from '../../components/DialogProvider'
import { useSubscriptable } from '../../services/subscriptable'
import TypificationDialog from './TypificationDialog'

function CallLockButton() {
  const autoRefresh = CallInfo.autoRefresh.use()
  return (
    <IconButton
      className="btn-lock"
      title={
        autoRefresh ? 'Actualitza el cas automàticament' : 'Fixa el cas actual'
      }
      onClick={() => {
        CallInfo.autoRefresh.toggle()
      }}
    >
      <div className="icon-lock">
        {autoRefresh ? (
          <i className="fas fa-lock-open" />
        ) : (
          <i className="fas fa-lock" />
        )}
      </div>
    </IconButton>
  )
}
function NewTabButton() {
  return (
    <IconButton
      className="btn-new-tab"
      title={'Obre una nova pestanya'}
      onClick={() => {
        window.open(window.location, '_blank')
      }}
    >
      <div className="icon-new-tab">
        <i className="fas fa-external-link-alt" />
      </div>
    </IconButton>
  )
}
function AnnotationButton() {
  const [openDialog, closeDialog] = useDialog()

  return (
    <IconButton
      title={'Anota la trucada fent servir aquest contracte'}
      onClick={() => {
        const oldAutoRefresh = CallInfo.autoRefresh()
        CallInfo.autoRefresh(false)
        function onClose() {
          CallInfo.autoRefresh(oldAutoRefresh)
          closeDialog()
        }
        openDialog({
          children: <TypificationDialog onClose={onClose} />,
        })
      }}
      disabled={CallInfo.savingAnnotation || Auth.username() === ''}
    >
      <div className="icon-clipboard">
        <i className="far fa-clipboard" />
      </div>
    </IconButton>
  )
}

function FormatedCall({ info }) {
  var time = new Date(info.date).toLocaleTimeString()
  return (
    <>
      <span className="time">{time}</span>
      &nbsp;
      <span className="phone">
        {info.phone ? info.phone : 'Registre Manual'}
      </span>
      &nbsp;&nbsp;
      {info.reason && (
        <span className="partner" title="Persona Atesa">
          {info.partner ? info.partner : 'Sense informació'}
        </span>
      )}
      {info.reason && info.contract && (
        <>
          &nbsp;
          <span className="contract" title="Contracte">
            {info.contract}
          </span>
        </>
      )}
      {!info.reason ? (
        <span className="pending">{"Pendent d'anotar"}</span>
      ) : (
        ''
      )}
    </>
  )
}

function CallEntry({ item, disabled }) {
  const currentCall = useSubscriptable(CallInfo.currentCall)
  const isSelected = item.date === currentCall
  const solved = item.reason !== ''
  const itemClicked = function (ev) {
    if (item.reason !== '') return
    CallInfo.toggleLog(item.date, item.phone)
  }
  return (
    <ListItem
      key={item.date}
      className={'registres' + (isSelected ? ' selected' : '')}
      selected={isSelected}
      disabled={disabled}
      onClick={solved ? undefined : itemClicked}
      button={!solved}
    >
      <ListItemText
        primary={<FormatedCall info={item} />}
        secondary={
          <span
            style={{
              display: 'block',
              whiteSpace: 'nowrap',
              textOverflow: 'ellipsis',
              overflow: 'hidden',
            }}
          >
            {item.reason}
          </span>
        }
        title={item.reason}
      />
    </ListItem>
  )
}

function AttendedCallList() {
  const personCalls = CallInfo.personCalls.use()
  if (personCalls === undefined)
    return (
      <Stack
        sx={{
          height: '20rem',
          width: '100%',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <CircularProgress />
      </Stack>
    )
  if (personCalls.length === 0) {
    return (
      <Box className="attended-calls-list">
        <List dense={true}>
          <ListItem className="registres">{'Cap trucada al registre'}</ListItem>
        </List>
      </Box>
    )
  }
  var currentDate = new Date().toLocaleDateString()
  return (
    <Box className="attended-calls-list">
      <List dense={true}>
        {personCalls
          .slice(0)
          .reverse()
          .map(function (item, index) {
            var needsDate = false
            var itemDate = new Date(item.date).toLocaleDateString()
            var itemWeekDay = new Date(item.date).toLocaleDateString(
              undefined,
              {
                weekday: 'long',
              },
            )
            if (itemDate !== currentDate) {
              currentDate = itemDate
              needsDate = true
            }
            return (
              <React.Fragment key={item.date}>
                {needsDate && (
                  <ListSubheader className="registres dateseparator">
                    {itemWeekDay + ' ' + itemDate}
                  </ListSubheader>
                )}
                <CallEntry item={item} />
              </React.Fragment>
            )
          })}
      </List>
    </Box>
  )
}
export default function AttendedCalls({ data }) {
  return (
    <Card className="card-attended-calls">
      <CardHeader
        title={'Trucades ateses'}
        action={
          <Stack direction="row">
            <CallLockButton />
            <NewTabButton />
            <AnnotationButton />
          </Stack>
        }
      ></CardHeader>
      <CardContent>
        <AttendedCallList />
      </CardContent>
    </Card>
  )
}
