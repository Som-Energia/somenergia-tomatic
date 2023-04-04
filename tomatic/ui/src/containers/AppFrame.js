import * as React from 'react'
import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import Menu from '@mui/material/Menu'
import MenuIcon from '@mui/icons-material/Menu'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import Container from '@mui/material/Container'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import appBackground from '../images/tomatic_bg.jpg'
import appLogo from '../images/tomatic-logo-24.png'
import SnackbarLogger from '../components/SnackbarLogger'
import ProfileButton from '../components/ProfileButton'
import LoginRequired from '../containers/LoginRequired'
import { Link } from 'react-router-dom'
import extraMenuOptions from '../services/extramenu'

const pages = ['Graelles', 'Centraleta', 'Persones', 'Trucada']
const appTitle = 'Tomàtic - Som Energia'

function ResponsiveAppBar({ children }) {
  const [anchorElNav, setAnchorElNav] = React.useState(null)

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget)
  }
  const handleCloseNavMenu = () => {
    setAnchorElNav(null)
  }

  const [anchorElMenu, setAnchorElMenu] = React.useState(null)

  const handleOpenMenu = (event) => {
    setAnchorElMenu(event.currentTarget)
  }
  const handleCloseMenu = () => {
    setAnchorElMenu(null)
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
                    component={Link}
                    to={`/${page}`}
                    key={page.title}
                    onClick={() => {
                      handleCloseNavMenu()
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
                  component={Link}
                  to={`/${page}`}
                  onClick={() => {
                    handleCloseNavMenu()
                  }}
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
            <ProfileButton />
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
                {extraMenuOptions().map((option, i) => (
                  <MenuItem
                    key={i}
                    onClick={() => {
                      handleCloseMenu()
                      option.action()
                    }}
                  >
                    <ListItemIcon>{option.icon}</ListItemIcon>
                    <Typography textAlign="center">{option.title}</Typography>
                  </MenuItem>
                ))}
              </Menu>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>
      <LoginRequired>{children}</LoginRequired>
      <SnackbarLogger />
    </>
  )
}
export default ResponsiveAppBar
