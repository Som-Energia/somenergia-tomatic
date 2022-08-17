#!/usr/bin/env python


import sys
import requests
import yaml
from emili import sendMail 
from io import open
from yamlns import namespace as ns
import dbconfig

execution_id = sys.argv[1]

config = ns.load('config.yaml')

template = """\
No he pogut completar la graella per la setmana.

- Execucio: {status.name}
- Compleció: {status.completedCells} / {status.totalCells}
- Penalitzacions: {status.solutionCost}
- Cel·la de bloqueig: {status.unfilledCell}
- [Revisar la graella]({config.baseUrl}/api/planner/solution/{execution_id})
- [Mirar la sortida]({config.baseUrl}/api/planner/status/{execution_id})

Podría ser un error, que sortiria en vermell a la sortida,
o, podria ser que ha estat executant-se i no l'ha trobada.
En el segon cas, proveu de posar menys torns,
canviar l'ordre de cerca dels dies de la setmana,
perque ompli els dies complicats primer.

El torn que no pot omplir, hi havia aquestes
indisponibilitats fortes.
Si es poguessin canviar a opcionals potser trobarà solució.

{status.busyReasons}
"""


def api(uri):
    response = requests.get(config.baseUrl + uri)
    if response.status_code != 200:
        raise Exception(
            f"While fetching {config.baseUrl}{uri}\n"
            f"{response.status_code}: {str(response.content, 'utf8')}"
        )
    return ns.loads(response.content)

statusuri = f"/api/planner/api/status/{execution_id}"
stopuri = f"/api/planner/api/stop/{execution_id}"
uploaduri = f"/api/planner/api/upload/{execution_id}"
killuri = f"/api/planner/api/kill/{execution_id}"

status = api(statusuri)
print(status.dump())
if status.get('status') != 'Stopped':
    stop = api(stopuri).get('ok')
    if not stop:
        kill = api(killuri)

if status.unfilledCell == "Complete":
    response = api(uploaduri)
    if response.get('ok')!=True:
        pass # TODO: ERROR
else:
    sendMail(
        sender=dbconfig.tomatic.dailystats.sender,
        to=dbconfig.tomatic.dailystats.recipients,
        subject="ERROR: Graella setmanal sense solució {execution_id}",
        md=template.format(
            execution_id=execution_id,
            config=config,
            status=status,
        ),
        config='dbconfig.py',
        verbose=True,
    )





