import React from 'react'
import Box from '@mui/material/Box'
import Menu from '@mui/material/Menu'
import MenuItem from '@mui/material/MenuItem'
import Typography from '@mui/material/Typography'
import IconButton from '@mui/material/IconButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import { useNavigate } from 'react-router-dom'
import { useDialog } from './DialogProvider'
import EmulateCallDialog from './EmulateCallDialog'
import TomaticSaysDialog from './TomaticSaysDialog'
import Tomatic from '../services/tomatic'

const scriptLauncherBase =
  window.location.protocol + '//' + window.location.hostname + ':5000'

export default function ExtraMenu() {
  const [anchorElMenu, setAnchorElMenu] = React.useState(null)
  const [openDialog, closeDialog] = useDialog()
  const navigate = useNavigate()

  function openCallEmulationDialog() {
    openDialog({
      children: <EmulateCallDialog {...{ closeDialog }} />,
    })
  }

  function openTomaticSaysDialog() {
    openDialog({
      children: <TomaticSaysDialog {...{closeDialog}} />
    })
  }

  const handleOpenMenu = (event) => {
    setAnchorElMenu(event.currentTarget)
  }
  const handleCloseMenu = () => {
    setAnchorElMenu(null)
  }

  const options = function () {
    return [
      {
        icon: '🕜',
        title: 'Planificador de Graelles',
        route: '/planner',
      },
      {
        icon: '📌',
        title: 'Torns fixes',
        route: '/ForcedTurns',
      },
      {
        icon: '🦸‍♀️',
        title: "Administració d'usuàries",
        route: '/Administration',
      },
      {
        icon: '📢',
        title: 'En Tomàtic diu...',
        action: openTomaticSaysDialog,
      },
      {
        icon: '📊',
        title: 'Estadístiques de trucades',
        action: function () {
          const url = scriptLauncherBase + '/runner/statshistory'
          window.open(url, '_blank')
        },
      },
      {
        icon: '🔄',
        title: 'Restableix els torns a la cua',
        action: function () {
          const url = scriptLauncherBase + '/runner/reloadqueue'
          window.open(url, '_blank')
        },
      },
      {
        icon: '🚀',
        title: 'Altres scripts de Centraleta',
        action: function () {
          const url = scriptLauncherBase
          window.open(url, '_blank')
        },
      },
      {
        icon: '🏷️',
        title: 'Anotacions: Actualitza categories',
        action: function () {
          // TODO: Call the api
        },
      },
      {
        icon: '🤙',
        title: 'Emula trucada entrant',
        action: () => {
          openCallEmulationDialog()
        },
      },
      {
        icon: '😎',
        title: 'Kumato mode',
        action: function () {
          Tomatic.toggleKumato()
        },
      },
      {
        icon: '🛟',
        navigation: true,
        title: "Guies d'usuaria i videos",
        action: function () {
          const url =
            'https://github.com/Som-Energia/somenergia-tomatic/blob/master/doc/userguide.md'
          window.open(url, '_blank')
        },
      },
    ]
  }

  return (
    <Box>
      <IconButton
        size="large"
        aria-label={'Extra functionalities'}
        aria-controls="menu-extra"
        aria-haspopup="true"
        onClick={handleOpenMenu}
        color="inherit"
      >
        <MoreVertIcon />
      </IconButton>
      <Menu
        id="menu-extra"
        anchorEl={anchorElMenu}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorElMenu)}
        onClose={handleCloseMenu}
      >
        {options().map((option, i) => (
          <MenuItem
            key={i}
            onClick={() => {
              handleCloseMenu()
              if (option.route) {
                navigate(option.route)
                return
              }
              option.action()
            }}
          >
            <ListItemIcon>{option.icon}</ListItemIcon>
            <Typography textAlign="center">{option.title}</Typography>
          </MenuItem>
        ))}
      </Menu>
    </Box>
  )
}
// vim: et ts=2 sw=2
