import * as React from 'react'
import { styled } from '@mui/material/styles'
import MuiAppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import Menu from '@mui/material/Menu'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth'
import SupportAgentIcon from '@mui/icons-material/SupportAgent'
import PeopleIcon from '@mui/icons-material/People'
import MenuIcon from '@mui/icons-material/Menu'
import PhoneCallbackIcon from '@mui/icons-material/PhoneCallback'
import appBackground_tomatic from '../images/tomatic_bg.jpg'
import appLogo from '../images/tomatic-logo-24.png'
import appLogo_pebrotic from '../images/pebrotic-logo-24.png'
import appLogo_ketchup from '../images/ketchup-logo-24.png'
import SnackbarMessages from '../components/SnackbarMessages'
import NavigationDrawer, { drawerWidth } from '../components/NavigationDrawer'
import ProfileButton from '../components/ProfileButton'
import ExtraMenu from '../components/ExtraMenu'
import LoginRequired from '../containers/LoginRequired'
import { Link } from 'react-router-dom'
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

const variantTitle = {
  tomatic: 'Tomàtic - Som Energia',
  pebrotic: 'Pebròtic - Som Energia',
  ketchup: 'Ketchup - Som Energia',
}

const variantLogo = {
  tomatic: appLogo,
  pebrotic: appLogo_pebrotic,
  ketchup: appLogo_ketchup,
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
      md: drawerWidth,
    },
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}))

function ResponsiveAppBar({ children }) {
  const isKumatoMode = Tomatic.isKumatoMode.use()
  const variant = Tomatic.variant.use()
  const [anchorElNav, setAnchorElNav] = React.useState(null)
  const [drawerOpen, setDrawerOpen] = React.useState(false)

  const appTitle = variantTitle[variant] || variantTitle['tomatic']
  const appLogo = variantLogo[variant] || variantLogo['tomatic']

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget)
  }
  const handleCloseNavMenu = () => {
    setAnchorElNav(null)
  }

  React.useEffect(() => {
    document.title = appTitle
  }, [appTitle])

  React.useEffect(() => {
    let link = document.querySelector("link[rel~='icon']")
    if (!link) {
      link = document.createElement('link')
      link.rel = 'icon'
      document.getElementsByTagName('head')[0].appendChild(link)
    }
    link.href = appLogo
  }, [appLogo])

  return (
    <Box id="tomatic" className={'main variant-' + variant}>
      <AppBar
        position="sticky"
        sx={{
          backgroundImage: `var(--banner)`,
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
              textShadow: '2pt 2pt black',
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
              textShadow: '2pt 2pt black',
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
          <ExtraMenu />
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
        className={isKumatoMode ? 'kumato-mode' : ''}
        component="main"
        sx={{
          minHeight: "calc(100vh - 70px)",
          flexGrow: 1,
          paddingLeft: {
            xs: 0,
            md: drawerOpen ? drawerWidth + 'px' : 'calc(60px + 4pt)',
          },
        }}
      >
        <LoginRequired>{children}</LoginRequired>
      </Box>
      <SnackbarMessages variant="filled"/>
    </Box>
  )
}
export default ResponsiveAppBar
