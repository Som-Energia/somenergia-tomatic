// Dialog provider enables imperative dialog opening
// avoiding keeping dialog opening state.
// Children can access useDialog() custom hook which
// provides openDialog and closeDialog functions.
// The first one appends the provided component
// as direct child of the Provider.

// based on https://stackoverflow.com/questions/63737526/material-ui-how-to-open-dialog-imperatively-programmatically/63737527#63737527

import React from 'react'
import Dialog from '@mui/material/Dialog'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import DialogActions from '@mui/material/DialogActions'
import Button from '@mui/material/Button'
import Grow from '@mui/material/Grow'
import useMediaQuery from '@mui/material/useMediaQuery'
import { useTheme } from '@mui/material/styles'

const no_function = () => {}

const DialogContext = React.createContext([no_function, no_function])

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Grow ref={ref} {...props} />
})

function DialogContainer(props) {
  const {
    children,
    open,
    onClose,
    onKill,
    fullScreenBelow = 'md',
    ...extraprops
  } = props
  const theme = useTheme()
  const fullScreen = useMediaQuery(theme.breakpoints.down(fullScreenBelow))

  return (
    <Dialog
      TransitionComponent={Transition}
      TransitionProps={{
        onExited: onKill,
      }}
      open={open}
      onClose={onClose}
      fullScreen={fullScreen}
      scroll="paper"
      {...extraprops}
    >
      {children}
    </Dialog>
  )
}

export default function DialogProvider({ children }) {
  const [dialogs, setDialogs] = React.useState([])
  const createDialog = (option) => {
    const dialog = { ...option, open: true }
    setDialogs((dialogs) => [...dialogs, dialog])
  }

  const closeDialog = (...args) => {
    setDialogs((dialogs) => {
      const latestDialog = dialogs.pop()
      if (!latestDialog) return dialogs
      if (latestDialog.onClose) latestDialog.onClose(...args)
      return [...dialogs].concat({ ...latestDialog, open: false })
    })
  }
  const contextValue = React.useRef([createDialog, closeDialog])

  return (
    <DialogContext.Provider value={contextValue.current}>
      {children}
      {dialogs.map((dialog, i) => {
        const { onClose, ...dialogParams } = dialog
        const handleKill = () => {
          if (dialog.onExited) dialog.onExited()
          setDialogs((dialogs) => dialogs.slice(0, dialogs.length - 1))
        }

        return (
          <DialogContainer
            key={i}
            onClose={closeDialog}
            onKill={handleKill}
            {...dialogParams}
          />
        )
      })}
    </DialogContext.Provider>
  )
}

/**
This hook returns a function to open a confirmation dialog.
The returned function returns a Promise that will be resolved
or reject as the dialog is.


const userConfirmation = useConfirmationDialog()

function handleClick() {
    userConfirmation({
      title: "Proceed?",
      children: "Do you want to proceed?",
    })
    .then(()=> whatever)
    .catch(()=> undo stuff )
  }
*/
export function useConfirmationDialog() {
  const [openDialog, closeDialog] = useDialog()
  function userConfirmation({ title, body, proceedButton, abortButton }) {
    let resolvePromise
    let rejectPromise
    const promise = new Promise((resolve, reject) => {
      resolvePromise = resolve
      rejectPromise = reject
    })
    function abort() {
      closeDialog()
      rejectPromise(false)
    }
    function proceed() {
      resolvePromise(true)
      closeDialog()
    }
    openDialog({
      closeDialog: abort,
      children: (
        <>
          <DialogTitle>{title}</DialogTitle>
          <DialogContent>{body}</DialogContent>
          <DialogActions>
            <Button children={'Aborta'} {...abortButton} onClick={abort} />
            <Button
              variant="contained"
              children={'Procedeix'}
              {...proceedButton}
              onClick={proceed}
            />
          </DialogActions>
        </>
      ),
    })
    return promise
  }
  return userConfirmation
}

export const useDialog = () => React.useContext(DialogContext)
