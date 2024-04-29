import React from 'react'
import { MuiMarkdown } from 'mui-markdown'
import Paper from '@mui/material/Paper'

const text = `
Marcar indisponibilitats evita que se'ns assignin torns en hores en què no podem fer atenció

- Les **indisponibilitats** entraran en vigor en la següent graella que es generi.
  Per gestionar indisponibilitats de **graelles ja publicades**, consulteu el
  [Protocol Impossibilitat de realitzar les tasques del Servei d’Atenció i Suport](https://docs.google.com/document/d/1povOC1mF122Ed4La5YlzyxLiJyMgdIUR1FMdSSuLTVo)
- Les indisponibilitats **són una eina auto-gestionada per cuidar-nos**;
  cuidem també a les companyes que hauran de cobrir el nostre forat. 
- Marqueu-les com a 'Opcional' sempre que sigui possible:
  Ens permeten cobrir torns en cas necessari. 
- Elimineu les indisponibilitats obsoletes:
    - Ex: reunions de GTTs finalitzats o d'equips on ja no hi som. 
    - Indicar un motiu entenedor també ens ajuda a detectar aquests casos.
    - Contribueix a respectar els torns fixes
- Les **baixes o vacances anotades a l’Odoo** ja es veuen reflexades a la graella;
  no cal marcar-les com indisponibilitats
`

export default function BusyNotes() {
  return (
    <Paper sx={{ p: 1 }}>
      <MuiMarkdown>{text}</MuiMarkdown>
    </Paper>
  )
}
