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
import tomaticAvatar from '../images/tomatic-logo.png'
import Auth from '../services/auth'

function SimpleCard(props) {
  const { title, error, content, button, action } = props

  return (
    <Box
      sx={{
        display: 'flex',
        maxHeight: 'calc(100vh - 8em)',
      }}
    >
      <Card
        sx={{
          maxWidth: 'min(80%, 40rem)',
          marginBlock: '5vh',
          marginInline: 'auto',
        }}
      >
        <CardContent>
          <CardHeader
            title={title}
            titleTypographyProps={{
              variant: 'h4',
            }}
            subheader={content}
            subheaderTypographyProps={{
              variant: 'body1',
            }}
            avatar={
              <Avatar
                variant="rounded"
                sx={{ width: 100, height: 100 }}
                src={tomaticAvatar}
              ></Avatar>
            }
          ></CardHeader>
          {error && <Typography color="error">{`Error: ${error}`}</Typography>}
        </CardContent>
        <CardActions>
          <Button sx={{ ml: 'auto' }} onClick={action}>
            {button}
          </Button>
        </CardActions>
      </Card>
    </Box>
  )
}

export default function LoginRequired({ children }) {
  const auth = React.useContext(AuthContext)
  if (auth?.userid) return children
  return (
    <SimpleCard
      title={'Es requereix identificació'}
      error={Auth.error()}
      content={
        "Cal que us identifiqueu a Can Google amb l'usuari de Som Energia."
      }
      button={'Ves-hi!'}
      action={Auth.authenticate}
    />
  )
}
