// ProfileButton
// The button in the toolbar that enables login when logged out
// and access to profile options when logged in.
import * as React from 'react'

import Avatar from '@mui/material/Avatar'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import Menu from '@mui/material/Menu'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Tooltip from '@mui/material/Tooltip'
import MenuItem from '@mui/material/MenuItem'
import Divider from '@mui/material/Divider'
import ListItemIcon from '@mui/material/ListItemIcon'
import IconSettings from '@mui/icons-material/Settings'
import IconEventBusy from '@mui/icons-material/EventBusy'
import IconLogout from '@mui/icons-material/Logout'
import IconKumato from '@mui/icons-material/SettingsBrightness'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import Tomatic from '../services/tomatic'
import Auth from '../services/auth'
import { contrast } from '../services/colorutils'
import AuthContext from '../contexts/AuthContext'
import PersonEditor from './PersonEditor'
import { useDialog } from './DialogProvider'
import { CopyCalendarDialog } from './CopyCalendarDialog'
import EmulateCallDialog from './EmulateCallDialog'
import { useNavigate } from 'react-router-dom'

function ProfileButton() {
  const navigate = useNavigate()
  const [openDialog, closeDialog] = useDialog()
  const { userid, fullname, initials, color, avatar } =
    React.useContext(AuthContext)
  const [anchorElUser, setAnchorElUser] = React.useState(null)

  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget)
  }
  const handleCloseUserMenu = () => {
    setAnchorElUser(null)
  }

  function openBusyPage(person) {
    navigate(`/Indisponibilitats/${person}`)
  }

  function openCalendarDialog(username) {
    openDialog({
      children: <CopyCalendarDialog {...{ closeDialog, username }} />,
    })
  }

  function openCallEmulationDialog() {
    openDialog({
      children: <EmulateCallDialog {...{ closeDialog }} />,
    })
  }

  function openPersonEditorDialog() {
    openDialog({
      children: (
        <PersonEditor
          onClose={closeDialog}
          onSave={(id, data) => {
            Tomatic.setPersonDataReact(id, data)
            closeDialog()
          }}
          person={Tomatic.personFields(Auth.username())}
          allGroups={Tomatic.allGroups()}
          tables={Tomatic.tableOptions()}
        />
      ),
    })
  }

  const menuProfile = [
    {
      text: 'Perfil',
      icon: <IconSettings />,
      onclick: () => {
        openPersonEditorDialog()
      },
    },
    {
      text: 'Indisponibilitats',
      icon: <IconEventBusy />,
      onclick: () => {
        openBusyPage(Auth.username())
      },
    },
    {
      text: 'Exporta calendari',
      icon: <CalendarMonthIcon />,
      onclick: () => {
        openCalendarDialog(Auth.username())
      },
    },
    {
      text: 'Kumato mode',
      icon: <IconKumato />,
      onclick: Tomatic.toggleKumato,
    },
    {
      text: 'Emula trucada entrant',
      icon: '🤙',
      onclick: () => {
        openCallEmulationDialog()
      },
    },
    {
      text: 'Logout',
      icon: <IconLogout />,
      onclick: Auth.logout,
    },
  ]

  return (
    <Box sx={{ flexGrow: 0 }}>
      {userid ? (
        <>
          <Tooltip title={'Perfil'}>
            <IconButton
              onClick={handleOpenUserMenu}
              sx={{
                p: 0,
              }}
            >
              <Avatar
                alt={initials}
                src={avatar}
                sx={{
                  bgcolor: color,
                  color: contrast(color),
                }}
              >
                {initials}
              </Avatar>
            </IconButton>
          </Tooltip>
          <Menu
            sx={{
              mt: '45px',
            }}
            id="menu-appbar"
            anchorEl={anchorElUser}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorElUser)}
            onClose={handleCloseUserMenu}
          >
            <MenuItem onClick={handleCloseUserMenu}>
              <ListItemIcon>
                <Avatar
                  sx={{
                    width: 24,
                    height: 24,
                    bgcolor: color,
                    color: contrast(color),
                  }}
                />
              </ListItemIcon>
              {fullname}
            </MenuItem>
            <Divider />
            {menuProfile.map((option, i) => (
              <MenuItem
                key={i}
                onClick={() => {
                  option.onclick && option.onclick()
                  handleCloseUserMenu()
                }}
              >
                <ListItemIcon>{option.icon}</ListItemIcon>
                <Typography textAlign="center">{option.text}</Typography>
              </MenuItem>
            ))}
          </Menu>
        </>
      ) : (
        <Button variant="contained" onClick={Auth.authenticate}>
          {"IDENTIFICA'T"}
        </Button>
      )}
    </Box>
  )
}

export default ProfileButton
