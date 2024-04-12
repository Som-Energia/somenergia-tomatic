import Stack from '@mui/material/Stack'
import Box from '@mui/material/Box'

export default function Solo({ className, children, ...props }) {
  return (
    <Box className={className}>
      <Stack
        direction="column"
        alignItems="center"
        justifyContent="center"
        {...props}
      >
        {children}
      </Stack>
    </Box>
  )
}
