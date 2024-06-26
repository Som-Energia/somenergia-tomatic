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
import Tomatic from '../services/tomatic'
import avatarTomatic from '../images/tomatic-logo.png'
import avatarPebrotic from '../images/pebrotic-logo.png'
import avatarKetchup from '../images/ketchup-logo.png'

const avatarByVariant = {
  tomatic: avatarTomatic,
  pebrotic: avatarPebrotic,
  ketchup: avatarKetchup,
}

export default function SimpleCard(props) {
  const { title, error, content, button, action } = props
  const variant = Tomatic.variant.use()

  const avatar = avatarByVariant[variant] || avatarTomatic

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
                src={avatar}
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
