#!/usr/bin/env python

import click
from consolemsg import fail, step
from datetime import datetime, timedelta
from pathlib import Path
from yamlns.dateutils import Date
from yamlns import ns
from tomatic import schedulestorage
from tomatic.plannerexecution import PlannerExecution, nextMonday
from tomatic.retriever import downloadIdealLoad
from tomatic.persons import update as updatePerson

@click.group()
def cli():
    pass

@cli.command()
def importidealload():
    """
    Takes the ideal shift load from the drive document (to be deprecated)
    and imports it into tomatic persons.yaml file.
    """
    import dbconfig
    config = ns.load("config.yaml")
    config.idealshifts = "idealshifts.yaml"
    downloadIdealLoad(config)
    loads = ns.load(config.idealshifts)
    del persons()['loads']
    for person, load in loads.items():
        updatePerson(person, ns(load=load))

@cli.command()
def retireold():
    schedules = schedulestorage.Storage()
    today = datetime.today()
    twoMondaysAgo = str((today - timedelta(days=today.weekday()+7*2)).date())
    step("Retiring timetables older than {}", twoMondaysAgo)
    schedules.retireOld(twoMondaysAgo)

@cli.command()
@click.argument(
    'yaml',
    type=Path,
)
def upload():
    schedules = schedulestorage.Storage()
    step("uploading {}".format(yaml))
    graella = ns.load(yaml)
    logmsg = (
        "{}: {} ha pujat {} ".format(
        datetime.now(),
        "tomatic",
        graella.week,
        ))
    graella.setdefault('log',[]).append(logmsg)
    schedules.save(graella)
    schedulestorage.publishStatic(graella)

@cli.command()
@click.argument(
    'monday',
    type=Date,
)
def launch(monday):
    import requests
    from emili import sendMail 
    import dbconfig
    import time
    import uuid

    config = ns.load('config.yaml')
    minutes = dbconfig.tomatic.get('plannerGraceTime', 2*60)

    step(f"Timetables: Lauching timetable for {monday}")
    execution_id = PlannerExecution.start(
        nlines=config.nTelefons,
        monday=str(monday),
        description='llençada-automatica-{}'.format(uuid.uuid4()),
    )

    step(f"Timetables: Sleeping for {minutes} minutes until completition")
    time.sleep(minutes*60)
    step(f"Timetables: Stop sleeping after {minutes} minutes")

    execution = PlannerExecution(execution_id)
    status = execution.listInfo()
    print(status.dump())

    if status.get('status') != 'Stopped':
        step("Timetables: Still running, stopping")
        stop = execution.stop()
        if not stop:
            step("Timetables: Still running, killing")
            kill = execution.kill()

    if status.unfilledCell == "Complete":
        step("Timetables: Complete, uploading")
        execution.upload('tomatic')
        return

    step("Timetables: Incomplete, sending report email")

    busy='\n'.join([
        f'- **{person}:** ' + ', '.join(reasons)
        for person, reasons in status.busyReasons.items()
    ])

    failure_template = """\
No he pogut generar la graella per la setmana del {monday}.

- Execucio: {status.name}
- Compleció: {status.completedCells} / {status.totalCells}
- Penalitzacions: {status.solutionCost}
- Cel·la de bloqueig: {status.unfilledCell}

{diagnosis}
"""

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
        md=failure_template.format(
            monday=monday,
            execution_id=execution_id,
            config=config,
            status=status,
            diagnosis=diagnosis,
        ),
        config='dbconfig.py',
        verbose=True,
    )

if __name__=='__main__':
    cli()

