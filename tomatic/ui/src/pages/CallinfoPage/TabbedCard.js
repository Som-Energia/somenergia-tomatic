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
  children,
}) {
  return (
    <Box
      className="partner-card"
      sx={{
        minWidth: '200px',
      }}
    >
      <Card className="card-info">
        <Box className="partner-tabs">
          <Tabs
            variant="scrollable"
            scrollButtons="auto"
            value={currentTab}
            onChange={(ev, value) => onTabChanged(value)}
            sx={{
              maxWidth: '465px',
            }}
          >
            {labels.map((label, i) => {
              return <Tab key={i} label={label} />
            })}
          </Tabs>
        </Box>
        <CardContent>
          {Inner && <Inner />}
          {children}
        </CardContent>
      </Card>
    </Box>
  )
}
