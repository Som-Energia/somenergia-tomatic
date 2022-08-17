#!/usr/bin/env python


import sys
import requests
from emili import sendMail 
from io import open
from yamlns import namespace as ns
import dbconfig
import time
import uuid
from consolemsg import step

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

config = ns.load('config.yaml')
monday = sys.argv[1]
minutes = 2

def apiPost(url, **params):
    response = requests.post(
        config.baseUrl + url,
        params=params,
    )

    if response.status_code != 200:
        raise Exception(
            f"While posting {params} to {config.baseUrl}{url}\n"
            f"{response.status_code}: {str(response.content, 'utf8')}"
        )
    return ns.loads(response.content)

def api(url):
    response = requests.get(
        config.baseUrl + url,
    )

    if response.status_code != 200:
        raise Exception(
            f"While getting {config.baseUrl}{url}\n"
            f"{response.status_code}: {str(response.content, 'utf8')}"
        )
    return ns.loads(response.content)

step("Timetables: Lauching timetable for {monday}")
result = apiPost('/api/planner/api/run',
    nlines=config.nTelefons,
    monday=monday,
    description='llençada-automatica-{}'.format(uuid.uuid4()),
)
execution_id = result.execution_id


statusuri = f"/api/planner/api/status/{execution_id}"
stopuri = f"/api/planner/api/stop/{execution_id}"
uploaduri = f"/api/planner/api/upload/{execution_id}"
killuri = f"/api/planner/api/kill/{execution_id}"

step("Timetables: Sleepning for {hours} hours until completition")
time.sleep(minutes*60)
step("Timetables: Sleepning for {hours} hours until completition")

status = api(statusuri)
print(status.dump())

if status.get('status') != 'Stopped':
    step("Timetables: Still running, stopping")
    stop = api(stopuri).get('ok')
    if not stop:
        step("Timetables: Still running, killing")
        kill = api(killuri)

if status.unfilledCell == "Complete":
    step("Timetables: Complete, uploading")
    response = api(uploaduri)
    if response.get('ok')!=True:
        pass # TODO: ERROR
    sys.exit()

step("Timetables: Inomplete, sending report email")
sendMail(
    sender=dbconfig.tomatic.dailystats.sender,
    to=['david.garcia@somenergia.coop'],
    #to=dbconfig.tomatic.dailystats.recipients,
    subject=f"ERROR: Graella setmanal sense solució {execution_id}",
    md=template.format(
        execution_id=execution_id,
        config=config,
        status=status,
    ),
    config='dbconfig.py',
    verbose=True,
)





