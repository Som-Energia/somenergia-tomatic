/**
SnackbarMessages is a message subscriber that display messages
pushed to the messages service as temporary Snackbars.

This way any code, even code outside React components can
push error messages that will be properly displayed.

Attributes:

- `autoHideDuration`: in ms time after which the snackbar will dissappear
- `vertical`: vertical position of the snackbars ('top', 'bottom', undefined)
- `horizontal`: horizontal position of the snackbars ('left', 'middle', 'right', undefined)
- `slideTo`: direction of the slide on appearing ('left', 'right', 'up', 'down', undefined),
  by default chooses the closest vertical direction ('up' for 'top', 'down' for 'bottom')
- `variant`: look variant ('standard', 'filled', 'outlined')
*/

import React from 'react'
import Snackbar from '@mui/material/Snackbar'
import Alert from '@mui/material/Alert'
import AlertTitle from '@mui/material/AlertTitle'
import Slide from '@mui/material/Slide'
import { subscribe } from '../services/messages'

// Unique message identifier to diferentiate all messages
let messageid = 0

export default function SnackbarMessages(props) {
  const {
    autoHideDuration = 5000,
    TransitionComponent = Slide,
    TransitionProps = undefined,
    vertical = 'bottom',
    horizontal = 'right',
    slideTo = 'left',
    variant = undefined,
    ...extra
  } = props
  const [messages, setMessages] = React.useState([])
  const [current, setCurrent] = React.useState(undefined)
  React.useEffect(() => {
    const unsubscribe = subscribe((incoming) => {
      setMessages((messages) => [...messages, { id: messageid++, ...incoming }])
    })
    return unsubscribe
  }, [])

  const handleClose = () => {
    setMessages((messages) => messages.splice(1))
  }
  return (
    <>
      {messages.map((message) => (
        <Snackbar
          open
          autoHideDuration={autoHideDuration}
          key={message.id}
          onClose={handleClose}
          TransitionComponent={TransitionComponent}
          {...(slideTo ? { TransitionProps: { direction: slideTo } } : {})}
          anchorOrigin={{ vertical, horizontal }}
          {...extra}
        >
          <Alert
            onClose={handleClose}
            variant={variant}
            severity={message.level || undefined}
            color={message.level === undefined ? 'primary' : undefined}
            sx={{
              // Some hack needed to avoid
              ...(message.level === undefined && variant === 'filled'
                ? { color: 'primary.contrastText' }
                : {}),
            }}
          >
            {message.context && <AlertTitle>{message.context}</AlertTitle>}
            {message.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  )
}
