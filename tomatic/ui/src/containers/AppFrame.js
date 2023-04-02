import * as React from 'react'
import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import Menu from '@mui/material/Menu'
import MenuIcon from '@mui/icons-material/Menu'
import Container from '@mui/material/Container'
import Avatar from '@mui/material/Avatar'
import Button from '@mui/material/Button'
import Tooltip from '@mui/material/Tooltip'
import MenuItem from '@mui/material/MenuItem'
import Divider from '@mui/material/Divider'
import ListItemIcon from '@mui/material/ListItemIcon'
import appBackground from '../images/tomatic_bg.jpg'
import appLogo from '../images/tomatic-logo-24.png'
import Tomatic from '../services/tomatic'
import Auth from '../services/auth'
import SnackbarLogger from '../components/SnackbarLogger'
import Settings from '@mui/icons-material/Settings'
import EventBusy from '@mui/icons-material/EventBusy'
import Logout from '@mui/icons-material/Logout'
import { contrast } from '../mithril/components/colorutils'

const pages = ['Graelles', 'Centraleta', 'Persones', 'Trucada']
const menuProfile = [
  {
    text: 'Perfil',
    icon: <Settings />,
  },
  {
    text: 'Indisponibilitats',
    icon: <EventBusy />,
  },
  {
    text: 'Logout',
    icon: <Logout />,
    onclick: Auth.logout,
  },
]
const appTitle = 'Tomàtic - Som Energia'

var updateUser = null
Auth.onUserChanged.push(() => updateUser && updateUser(Auth.username()))

function ResponsiveAppBar({ children }) {
  const [userid, setUserId] = React.useState(Auth.username())
  updateUser = setUserId
  const userName = Tomatic.formatName(userid)
  const userAvatarLetters = Tomatic.nameInitials(userid)
  console.log('Name initials', userAvatarLetters)
  const userColor = '#' + Tomatic.personColor(userid)
  const userAvatar = null
  //'https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50'

  const [anchorElNav, setAnchorElNav] = React.useState(null)
  const [anchorElUser, setAnchorElUser] = React.useState(null)

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget)
  }
  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget)
  }

  const handleCloseNavMenu = () => {
    setAnchorElNav(null)
  }

  const handleCloseUserMenu = () => {
    setAnchorElUser(null)
  }

  return (
    <>
      <AppBar
        position="sticky"
        sx={{
          backgroundImage: `url(${appBackground})`,
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right',
          backgroundColor: 'black',
        }}
      >
        <Container maxWidth="xl">
          <Toolbar disableGutters>
            <Box
              sx={{
                display: {
                  xs: 'none',
                  md: 'flex',
                },
                mr: 1,
              }}
            >
              <img alt={'Logo'} src={appLogo} />
            </Box>
            <Typography
              variant="h6"
              noWrap
              component="a"
              href="/"
              sx={{
                mr: 2,
                display: {
                  xs: 'none',
                  md: 'flex',
                },
                fontWeight: 700,
                letterSpacing: '.1rem',
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              {appTitle}
            </Typography>

            <Box
              sx={{
                flexGrow: 1,
                display: {
                  xs: 'flex',
                  md: 'none',
                },
              }}
            >
              <IconButton
                size="large"
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleOpenNavMenu}
                color="inherit"
              >
                <MenuIcon />
              </IconButton>
              <Menu
                id="menu-appbar"
                anchorEl={anchorElNav}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'left',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'left',
                }}
                open={Boolean(anchorElNav)}
                onClose={handleCloseNavMenu}
                sx={{
                  display: {
                    xs: 'block',
                    md: 'none',
                  },
                }}
              >
                {pages.map((page) => (
                  <MenuItem
                    key={page}
                    onClick={() => {
                      handleCloseNavMenu()
                      Tomatic.error(
                        'La funcionalitat encara no està implementada'
                      )
                    }}
                  >
                    <Typography textAlign="center">{page}</Typography>
                  </MenuItem>
                ))}
              </Menu>
            </Box>
            <Box
              sx={{
                display: {
                  xs: 'flex',
                  md: 'none',
                },
                mr: 1,
              }}
            >
              <img alt={'Logo'} src={appLogo} />
            </Box>
            <Typography
              variant="h5"
              noWrap
              component="a"
              href=""
              sx={{
                mr: 2,
                display: {
                  xs: 'flex',
                  md: 'none',
                },
                flexGrow: 1,
                fontWeight: 700,
                letterSpacing: '.3rem',
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              {appTitle}
            </Typography>
            <Box
              sx={{
                flexGrow: 1,
                display: {
                  xs: 'none',
                  md: 'flex',
                },
              }}
            >
              {pages.map((page) => (
                <Button
                  key={page}
                  onClick={handleCloseNavMenu}
                  sx={{
                    my: 2,
                    color: 'white',
                    backgroundColor: `rgba(0,0,0,.3)`,
                    display: 'block',
                    textShadow: '2pt 2pt black',
                  }}
                >
                  {page}
                </Button>
              ))}
            </Box>

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
                        <Typography textAlign="center">
                          {option.text}
                        </Typography>
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
          </Toolbar>
        </Container>
      </AppBar>
      {children}
      <SnackbarLogger />
    </>
  )
}
export default ResponsiveAppBar
