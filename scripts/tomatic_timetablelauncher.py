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
No he pogut generar la graella per la setmana del {monday}.

- Execucio: {status.name}
- Compleció: {status.completedCells} / {status.totalCells}
- Penalitzacions: {status.solutionCost}
- Cel·la de bloqueig: {status.unfilledCell}

{diagnosis}
"""

config = ns.load('config.yaml')
monday = sys.argv[1]
minutes = 2*60

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



step(f"Timetables: Lauching timetable for {monday}")
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

step(f"Timetables: Sleeping for {minutes} minutes until completition")
time.sleep(minutes*60)
step(f"Timetables: Stop sleeping after {minutes} minutes")

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

step("Timetables: Incomplete, sending report email")

busy='\n'.join([
    f'- **{person}:** ' + ', '.join(reasons)
    for person, reasons in status.busyReasons.items()
])

diagnosis = f"""\
La [graella]({config.baseUrl}/api/planner/solution/{execution_id}) està incomplerta.
El torn on m'encallo es a {status.unfilledCell}.

Pots provar [llençar-la a mà]({config.baseUrl}/api/planner) però:

- amb **menys línies** (sobretot si hi ha molts torns amb 'ningu')
- indicant que vols **omplir primer el dia** amb el torn complicat
- si encara es bloqueja, revisant les **indisponibilitats** del torn complicat

Les indisponibilitats no opcionals que afecten a aquest torn son:

{busy}
""" if status.unfilledCell else f"""\
No he arribat a farcir cap casella de la graella.
Segurament es deu a algun error de configuració.

Revisa el missatge al final de tot de [la sortida]({config.baseUrl}/api/planner/status/{execution_id}),
i si no es res que puguis interpretar tu mateixa,
reenvia aquest mateix correu a incidencies ({dbconfig.tomatic.supportmail}).
"""


sendMail(
    sender=dbconfig.tomatic.dailystats.sender,
    to=dbconfig.tomatic.dailystats.recipients,
    subject=f"ERROR: Graella setmanal sense solució {execution_id}",
    md=template.format(
        monday=monday,
        execution_id=execution_id,
        config=config,
        status=status,
        diagnosis=diagnosis,
    ),
    config='dbconfig.py',
    verbose=True,
)

