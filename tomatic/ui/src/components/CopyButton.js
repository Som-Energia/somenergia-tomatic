import * as React from 'react'
import Tooltip from '@mui/material/Tooltip'
import IconButton from '@mui/material/IconButton'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import CheckIcon from '@mui/icons-material/Check'

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export default function CopyButton({ text, ...props }) {
  const [copying, setCopying] = React.useState(false)
  async function copy() {
    setCopying(true)
    await navigator.clipboard.writeText(text)
    await sleep(1000)
    setCopying(false)
  }
  if (copying)
    return (
      <>
        <Tooltip placement="right" arrow title={'Copiat!'}>
          <IconButton variant="contained" color="success">
            <CheckIcon />
          </IconButton>
        </Tooltip>
      </>
    )
  return (
    <>
      <IconButton variant="contained" color="primary" onClick={copy} {...props}>
        <ContentCopyIcon />
      </IconButton>
    </>
  )
}
