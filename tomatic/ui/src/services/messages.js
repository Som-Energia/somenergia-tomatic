/**
Subscriptable source for log and error messages.

This module provides functions to send messages
and a function to receive such messages,
to decouple providers and consumers.

Sources of messages just call one of the message functions:

- error(message)
- warn(message)
- success(message)
- info(message)
- log(message)

Presenters of such messages subscribe() a function
that will receive message objects.

- `level`: 'error', 'warning', 'info', 'success' or undefined (for log)
- `message`: a string to be displayed

IMPORTANT: `subscribe()` returns a function to unsubscribe. Use it.

*/

const _subscribers = new Set()
function _notify(message, level, extra) {
  _subscribers.forEach((l) => l({ message, level, ...extra }))
}

function subscribe(subscriber) {
  _subscribers.add(subscriber)
  return () => _subscribers.delete(subscriber)
}

function log(message, extra) {
  _notify(message, undefined, extra)
}

function error(message, extra) {
  _notify(message, 'error', extra)
}

function warn(message, extra) {
  _notify(message, 'warning', extra)
}

function info(message, extra) {
  _notify(message, 'info', extra)
}

function success(message, extra) {
  _notify(message, 'success', extra)
}

// Default handler, use the console
const disableConsoleMessages = subscribe(({ message, level }) => {
  const actions = {
    log: () => console.log(message),
    error: () => console.error('Error:', message),
    warning: () => console.warn('Warning:', message),
    info: () => console.info('Info:', message),
    success: () => console.log('Success:', message),
  }[level || 'log']()
})

export { error, warn, success, info, log, subscribe, disableConsoleMessages }
const messages = {
  error,
  warn,
  success,
  info,
  log,
  subscribe,
  disableConsoleMessages,
}
export default messages
