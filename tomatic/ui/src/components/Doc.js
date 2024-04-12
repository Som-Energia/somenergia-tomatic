import React from 'react'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'

function Doc({message}) {
  return (
    <Card>
      <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          Info
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      </CardContent>
    </Card>
  )
}

export default Doc
