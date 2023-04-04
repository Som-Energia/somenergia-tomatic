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
import Tomatic from '../services/tomatic'
import Auth from '../services/auth'
import { contrast } from '../mithril/components/colorutils'
import AuthContext from '../contexts/AuthContext'
import editAvailabilities from '../mithril/components/busyeditor'

const menuProfile = [
  {
    text: 'Perfil',
    icon: <IconSettings />,
  },
  {
    text: 'Indisponibilitats',
    icon: <IconEventBusy />,
    onclick: () => {
      editAvailabilities(Auth.username())
    },
  },
  {
    text: 'Kumato mode',
    icon: <IconKumato />,
    onclick: Tomatic.toggleKumato,
  },
  {
    text: 'Logout',
    icon: <IconLogout />,
    onclick: Auth.logout,
  },
]

function ProfileButton() {
  const { userid, fullname, initials, color, avatar } =
    React.useContext(AuthContext)
  const [anchorElUser, setAnchorElUser] = React.useState(null)

  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget)
  }
  const handleCloseUserMenu = () => {
    setAnchorElUser(null)
  }

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
                  handleCloseUserMenu()
                  option.onclick && option.onclick()
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
