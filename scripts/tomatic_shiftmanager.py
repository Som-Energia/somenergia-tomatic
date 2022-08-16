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
        subject="ERROR: Generant la graelle setmanal {execution_id}",
        md=template.format(
            execution_id=execution_id,
            config=config,
            status=status,
        ),
        config='dbconfig.py',
        verbose=True,
    )





