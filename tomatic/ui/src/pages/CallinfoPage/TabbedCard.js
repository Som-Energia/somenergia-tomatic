import Box from '@mui/material/Box'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'

export default function TabbedCard({
  currentTab,
  onTabChanged,
  Inner,
  labels,
}) {
  return (
    <Box
      className="partner-card"
      sx={{
        maxWidth: '465px',
        minWidth: '200px',
      }}
    >
      <Box className="partner-tabs">
        <Tabs
          variant="scrollable"
          scrollButtons="auto"
          value={currentTab}
          onChange={(ev, value) => onTabChanged(value)}
        >
          {labels.map((label, i) => {
            return (
              <Tab
                key={i}
                label={label}
                sx={{
                  '&.Mui-selected': {
                    color: '#555',
                    bgcolor: '#ABD0AB',
                  },
                }}
              />
            )
          })}
        </Tabs>
      </Box>
      <Card className="card-info">
        <CardContent>
          <Inner />
        </CardContent>
      </Card>
    </Box>
  )
}
