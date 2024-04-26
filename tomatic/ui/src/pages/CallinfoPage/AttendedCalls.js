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
import Tooltip from '@mui/material/Tooltip'
import ContentPasteIcon from '@mui/icons-material/ContentPaste'
import LockOpenIcon from '@mui/icons-material/LockOpen'
import LockIcon from '@mui/icons-material/Lock'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import CallInfo from '../../contexts/callinfo'
import Auth from '../../services/auth'
import { useDialog } from '../../components/DialogProvider'
import { useSubscriptable } from '../../services/subscriptable'
import TypificationDialog from './TypificationDialog'
import { vat2nif } from '../../services/vat'

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
      {autoRefresh ? (
        <LockOpenIcon className="icon-lock" />
      ) : (
        <LockIcon className="icon-lock" />
      )}
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
      <OpenInNewIcon className="icon-new-tab" />
    </IconButton>
  )
}
function AnnotationButton() {
  const [openDialog, closeDialog] = useDialog()

  return (
    <IconButton
      title={'Anota la trucada seleccionada fent servir aquest contracte'}
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
      <ContentPasteIcon className="icon-clipboard" />
    </IconButton>
  )
}

function FormatedCall({ info }) {
  const categories = CallInfo.categories.use()
  const time = new Date(info.call_timestamp).toLocaleTimeString()
  const solved = info.category_ids.length !== 0
  const filtered_categories = categories.filter(({ id }) =>
    info.category_ids.includes(id),
  )
  return (
    <>
      <Stack direction="row" justifyContent="space-between" gap={1}>
        <span className="time">{time}</span>
        <span className="phone">
          {info.phone_number ? info.phone_number : 'Registre Manual'}
        </span>
        <Tooltip
          title={
            <>
              {filtered_categories.map((category, i) => (
                <Box key={i}>{`[${category.code}] ${category.name}`}</Box>
              ))}
            </>
          }
        >
          <span
            style={{
              textAlign: 'right',
              flex: 1,
              whiteSpace: 'nowrap',
              textOverflow: 'ellipsis',
              overflow: 'hidden',
              color: 'gray',
            }}
          >
            {filtered_categories.map((category, i) => (
              <React.Fragment key={i}>
                &nbsp;
                {category.code}
              </React.Fragment>
            ))}
          </span>
        </Tooltip>
      </Stack>
      <Stack direction="row" justifyContent="space-between" gap={1}>
        {solved && (
          <>
            <span
              className="partner"
              style={{
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
                overflow: 'hidden',
              }}
              title={info.caller_name}
            >
              {info.caller_name
                ? info.caller_name
                : info.caller_erp_id
                ? 'Nom no informat'
                : 'Persona no identificada'}
            </span>
            <span style={{ color: 'gray' }}>{vat2nif(info.caller_vat)}</span>
          </>
        )}
      </Stack>
      <Stack direction="row" justifyContent="space-between" gap={1}>
        {solved && info.contract_number && (
          <>
            <span
              className="contract"
              style={{
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
                overflow: 'hidden',
              }}
              title={info.contract_address}
            >
              {info.contract_address}
            </span>
            <span style={{ color: 'gray' }}>{info.contract_number}</span>
          </>
        )}
      </Stack>
      {!solved ? <Box className="pending">{"Pendent d'anotar"}</Box> : ''}
    </>
  )
}

function CallEntry({ item, disabled }) {
  const currentCall = useSubscriptable(CallInfo.currentCall)
  const isSelected = item.call_timestamp === currentCall
  const solved = item.category_ids.length !== 0
  const itemClicked = function (ev) {
    if (solved) return
    CallInfo.toggleLog(item.call_timestamp, item.phone_number)
  }
  return (
    <ListItem
      key={item.call_timestamp}
      className={'registres' + (isSelected ? ' selected' : '')}
      selected={isSelected}
      disabled={disabled}
      onClick={solved ? undefined : itemClicked}
      button={!solved}
    >
      <ListItemText
        primary={<FormatedCall info={item} />}
        title={item.comments}
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
            var itemDate = new Date(item.call_timestamp).toLocaleDateString()
            var itemWeekDay = new Date(item.call_timestamp).toLocaleDateString(
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
              <React.Fragment key={index}>
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
