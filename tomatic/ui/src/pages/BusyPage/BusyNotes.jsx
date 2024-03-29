import React from 'react'
import { MuiMarkdown } from 'mui-markdown'
import Paper from '@mui/material/Paper'

const text=`
##### Consideracions quan demanem indisponibilitats

- Les indisponibilitat serveixen per evitar que ens assignin torn d'atenció a certes hores.
- Són una eina per cuidar-nos. Sigueu generoses amb les companyes que hauran d'omplir el forat que deixeu.
- No cal apuntar vacances, baixes i festius. S'agafen de l'Odoo
- Apunteu: reunions, desplaçaments, conciliacions, treball concentrat, horaris atìpics...
- Marqueu-les com a 'Opcional' sempre que sigui possible
- Aneu eliminant les que ja no tinguin sentit
- Tenen efecte en el moment de generar la graella. Si ja està generada, caldria demanar un canvi amb les companyes
`

export default function BusyNotes() {
  return (
    <Paper sx={{ p: 1 }}>
    <MuiMarkdown>
      {text}
    </MuiMarkdown>
    </Paper>
  )
}


