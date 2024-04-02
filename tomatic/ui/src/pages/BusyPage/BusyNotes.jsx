import React from 'react'
import { MuiMarkdown } from 'mui-markdown'
import Paper from '@mui/material/Paper'

const text=`
Marcar indisponibilitats evita que ens assignin torns a hores que no podem, o no que ens van bé, de fer.

- Marqueu reunions, desplaçaments, conciliacions, treball concentrat, horaris atípics...
- No cal anotar vacances, baixes i festius, que ja són a l'Odoo.
- **Són una eina auto-gestionada per cuidar-nos**. Cuidem també a les companyes que hauran de cobrir el nostre forat.
- Marqueu-les com a 'Opcional' sempre que sigui possible.
    - Ens permet cobrir el torn si no hi ha ningú més disponible.
- Aneu eliminant les que deixin de tindre sentit:
    - Reunions de GTTs finalitzats, o d'equips on ja no hi som, portar al cole fills que ja van a la uni...
- Indicar un motiu entenedor també ens ajuda a detectar aquests casos.
- S'apliquen al moment de generar la graella. Si ja està generada, auto-gestioneu un canvi amb una companya.
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


