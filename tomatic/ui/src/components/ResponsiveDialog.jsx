import React from 'react'
import Dialog from '@mui/material/Dialog'
import useMediaQuery from '@mui/material/useMediaQuery'
import { useTheme } from '@mui/material/styles'

export default function ResponsiveDialog({
  onClose,
  scroll = 'paper',
  fullScreenBreak = 'sm',
  ...props
}) {
  const theme = useTheme()
  const fullScreen = useMediaQuery(theme.breakpoints.down(fullScreenBreak))
  // Having onClose always defined enables closing on Escape or on outside click
  function handleClose(...args) {
    return onClose && onClose(...args)
  }
  return (
    <Dialog
      scroll={scroll}
      fullScreen={fullScreen}
      onClose={handleClose}
      {...props}
    />
  )
}
