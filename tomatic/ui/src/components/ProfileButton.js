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
import Tomatic from '../services/tomatic'
import Auth from '../services/auth'
import { contrast } from '../mithril/components/colorutils'

const menuProfile = [
  {
    text: 'Perfil',
    icon: <IconSettings />,
  },
  {
    text: 'Indisponibilitats',
    icon: <IconEventBusy />,
  },
  {
    text: 'Logout',
    icon: <IconLogout />,
    onclick: Auth.logout,
  },
]

// TODO: This should be done in a context
var updateUser = null
Auth.onUserChanged.push(() => updateUser && updateUser(Auth.username()))

function ProfileButton() {
  const [userid, setUserId] = React.useState(Auth.username())
  const [anchorElUser, setAnchorElUser] = React.useState(null)
  updateUser = setUserId
  const userName = Tomatic.formatName(userid)
  const userAvatarLetters = Tomatic.nameInitials(userid)
  const userColor = '#' + Tomatic.personColor(userid)
  const userAvatar = null
  //'https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50'

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
                alt={userAvatarLetters}
                src={userAvatar}
                sx={{
                  bgcolor: userColor,
                  color: contrast(userColor),
                }}
              >
                {userAvatarLetters}
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
                    bgcolor: userColor,
                    color: contrast(userColor),
                  }}
                />
              </ListItemIcon>
              {userName}
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
