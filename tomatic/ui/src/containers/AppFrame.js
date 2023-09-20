import * as React from 'react'
import { styled } from '@mui/material/styles'
import MuiAppBar from '@mui/material/AppBar'
import CssBaseline from '@mui/material/CssBaseline'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import Menu from '@mui/material/Menu'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth'
import SupportAgentIcon from '@mui/icons-material/SupportAgent'
import PeopleIcon from '@mui/icons-material/People'
import MenuIcon from '@mui/icons-material/Menu'
import PhoneCallbackIcon from '@mui/icons-material/PhoneCallback'
import appBackground_tomatic from '../images/tomatic_bg.jpg'
import appBackground_pebrotic from '../images/pebrotic.jpg'
import appBackground_ketchup from '../images/ketchup.png'
import appLogo from '../images/tomatic-logo-24.png'
import SnackbarLogger from '../components/SnackbarLogger'
import NavigationDrawer, { drawerWidth } from '../components/NavigationDrawer'
import ProfileButton from '../components/ProfileButton'
import LoginRequired from '../containers/LoginRequired'
import { Link, useNavigate } from 'react-router-dom'
import extraMenuOptions from '../services/extramenu'
import Tomatic from '../services/tomatic'

const pages = [
  {
    icon: <CalendarViewMonthIcon />,
    text: 'Graelles',
  },
  {
    icon: <PeopleIcon />,
    text: 'Persones',
  },
  {
    icon: <SupportAgentIcon />,
    text: 'Centraleta',
  },
  {
    icon: <PhoneCallbackIcon />,
    text: 'Trucada',
  },
]

const variantBackground = {
  tomatic: appBackground_tomatic,
  pebrotic: appBackground_pebrotic,
  ketchup: appBackground_ketchup,
}

const variantTitle = {
  tomatic: 'Tomàtic - Som Energia',
  pebrotic: 'Pebròtic - Som Energia',
  ketchup: 'Tomàtic Ketchup - Som Energia',
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'drawerOpen',
})(({ theme, drawerOpen }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(drawerOpen && {
    zIndex: theme.zIndex.drawer - 1,
    marginLeft: drawerWidth,
    paddingLeft: {
      xs: 0,
      md: drawerOpen ? drawerWidth + 'px' : '60px',
    },
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}))

function ResponsiveAppBar({ children }) {
  const [anchorElNav, setAnchorElNav] = React.useState(null)
  const [drawerOpen, setDrawerOpen] = React.useState(false)
  const navigate = useNavigate()

  const appBackground =
    variantBackground[Tomatic.variant] || appBackground_tomatic
  const appTitle = variantTitle[Tomatic.variant] || variantTitle['tomatic']

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
    <Box sx={{ displah: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="sticky"
        sx={{
          backgroundImage: `url(${appBackground})`,
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right',
          backgroundColor: 'black',
        }}
        drawerOpen={drawerOpen}
      >
        <Toolbar disableGutters>
          <IconButton
            size="large"
            aria-label={'Open drawer'}
            aria-controls="drawer"
            onClick={() => setDrawerOpen(!drawerOpen)}
            edge="start"
            color="inherit"
            sx={{
              marginRight: 5,
              marginLeft: 1.3,
              ...{
                display: {
                  xs: 'none',
                  md: drawerOpen ? 'none' : 'flex',
                },
              },
            }}
          >
            <MenuIcon />
          </IconButton>
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
              {pages.map((page, index) => (
                <MenuItem
                  component={Link}
                  to={`/${page.text}`}
                  key={index}
                  onClick={() => {
                    handleCloseNavMenu()
                  }}
                >
                  <ListItemIcon>{page.icon}</ListItemIcon>
                  <Typography textAlign="center">{page.text}</Typography>
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
            {pages.map((page, index) => (
              <Button
                key={index}
                component={Link}
                to={`/${page.text}`}
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
                {page.text}
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
        </Toolbar>
      </AppBar>
      <NavigationDrawer
        id="drawer"
        items={pages}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{
          display: {
            xs: 'none',
            md: 'flex',
          },
        }}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          paddingLeft: {
            xs: 0,
            md: drawerOpen ? drawerWidth + 'px' : '60px',
          },
        }}
      >
        <LoginRequired>{children}</LoginRequired>
      </Box>
      <SnackbarLogger />
    </Box>
  )
}
export default ResponsiveAppBar
