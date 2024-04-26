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
import SellIcon from '@mui/icons-material/Sell'
import CommentIcon from '@mui/icons-material/Comment'
import CategoryChip from './CategoryChip'
import CallInfo from '../../contexts/callinfo'
import Auth from '../../services/auth'
import { useDialog } from '../../components/DialogProvider'
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

function FormatedCall({ call }) {
  const categories = CallInfo.categories.use()
  const time = new Date(call.call_timestamp).toLocaleTimeString()
  const solved = call.category_ids.length !== 0
  const filtered_categories = categories.filter(({ id }) =>
    call.category_ids.includes(id),
  )
  return (
    <>
      <Stack direction="row" justifyContent="space-between" gap={1}>
        <span className="time">{time}</span>
        <span className="phone">
          {call.phone_number ? call.phone_number : 'Registre Manual'}
        </span>
        <Stack direction="row" justifyContent="end" gap={1} flex={1}>
          {call.comments && (
            <Tooltip
              arrow
              sx={{ color: 'gray', alignText: 'right' }}
              title={<Box whiteSpace="pre-wrap">{call.comments}</Box>}
            >
              <CommentIcon />
            </Tooltip>
          )}
          {call.category_ids?.length ? (
            <Tooltip
              arrow
              sx={{
                color: 'gray',
                alignText: 'right',
                '& .MuiTooltip-tooltip': { maxWidth: 'none', bgcolor: 'red' },
              }}
              title={
                <>
                  {filtered_categories.map((category, i) => (
                    <CategoryChip key={i} size="small" {...{ category }} />
                  ))}
                </>
              }
            >
              <SellIcon />
            </Tooltip>
          ) : null}
        </Stack>
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
              title={call.caller_name}
            >
              {call.caller_name
                ? call.caller_name
                : call.caller_erp_id
                ? 'Nom no informat'
                : 'Persona no identificada'}
            </span>
            <span style={{ color: 'gray' }}>{vat2nif(call.caller_vat)}</span>
          </>
        )}
      </Stack>
      <Stack direction="row" justifyContent="space-between" gap={1}>
        {solved && call.contract_number && (
          <>
            <span
              className="contract"
              style={{
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
                overflow: 'hidden',
              }}
              title={call.contract_address}
            >
              {call.contract_address}
            </span>
            <span style={{ color: 'gray' }}>{call.contract_number}</span>
          </>
        )}
      </Stack>
      {!solved ? <Box className="pending">{"Pendent d'anotar"}</Box> : ''}
    </>
  )
}

function CallEntry({ call, disabled }) {
  const currentCall = CallInfo.currentCall.use()
  const isSelected = call.id === currentCall
  const solved = call.category_ids.length !== 0
  const itemClicked = function (ev) {
    if (solved) return
    CallInfo.toggleLog(call.call_timestamp, call.phone_number, call.id)
  }
  return (
    <ListItem
      key={call.call_timestamp}
      className={'registres' + (isSelected ? ' selected' : '')}
      selected={isSelected}
      disabled={disabled}
      onClick={solved ? undefined : itemClicked}
      button={!solved}
    >
      <ListItemText primary={<FormatedCall call={call} />} />
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
          .map(function (call, index) {
            var needsDate = false
            var itemDate = new Date(call.call_timestamp).toLocaleDateString()
            var itemWeekDay = new Date(call.call_timestamp).toLocaleDateString(
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
                <CallEntry call={call} />
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
