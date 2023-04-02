// LoginRequired
// An adapter for pages that require login.
// If not logged in, it shows a messages redirecting
// to login page.
import * as React from 'react'
import Card from '@mui/material/Card'
import CardHeader from '@mui/material/CardHeader'
import CardContent from '@mui/material/CardContent'
import CardActions from '@mui/material/CardActions'
import Button from '@mui/material/Button'
import Avatar from '@mui/material/Avatar'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import AuthContext from '../contexts/AuthContext'
//import tomaticAvatar from '../images/tomatic-avatar.png'
import tomaticAvatar from '../images/tomatic-logo.png'
import Auth from '../services/auth'

export default function LoginRequired({ children }) {
  const auth = React.useContext(AuthContext)
  if (auth?.userid) return children
  return (
    <Box
      sx={{
        display: 'flex',
        maxHeight: 'calc(100vh - 8em)',
      }}
    >
      <Card
        sx={{
          marginBlock: '5vh',
          marginInline: 'auto',
        }}
      >
        <CardContent>
          <CardHeader
            title={'Es requereix identificació!'}
            titleTypographyProps={{
              variant: 'h5',
            }}
            avatar={
              <Avatar
                variant="rounded"
                sx={{ width: 64, height: 64 }}
                src={tomaticAvatar}
              ></Avatar>
            }
          ></CardHeader>
          {Auth.error() && (
            <Typography color="error">{'Error: ' + Auth.error()}</Typography>
          )}
          <Typography>
            {
              "Cal que us identifiqueu a Can Google amb l'usuari de Som Energia."
            }
          </Typography>
        </CardContent>
        <CardActions>
          <Button sx={{ ml: 'auto' }} onClick={Auth.authenticate}>
            {'Ves-hi!'}
          </Button>
        </CardActions>
      </Card>
    </Box>
  )
}
