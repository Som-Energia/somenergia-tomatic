#!/usr/bin/env python

import click
from consolemsg import fail, step
from datetime import datetime, timedelta
from pathlib import Path
from yamlns.dateutils import Date
from yamlns import ns
from tomatic import schedulestorage
from tomatic.plannerexecution import PlannerExecution, nextMonday
from tomatic.persons import update as updatePerson, persons
import sys

@click.group()
def cli():
    pass

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
    'tsv',
    type=click.File("wt"),
    default=sys.stdout,
)
def workforce(tsv):
    from tomatic.retriever import addDays
    path_graelles = Path('graelles')

    graelles = sorted(
        # Retired timetables
        list(path_graelles.glob('old/graella-????-??-??.yaml')) +
        # Currently visible ones
        list(path_graelles.glob('graella-????-??-??.yaml')),
        # Sorted ignoring path, by date
        key=lambda x: x.name,
    )
    included = set()
    excluded = {'ningu', None, 'festiu', '?'}
    for graella in graelles:
        step("Processing {}".format(graella))
        timetable = ns.load(graella).timetable
        monday = Date(graella.stem[len('graella-'):])
        for i, weekday in enumerate(('dl', 'dm', 'dx', 'dj', 'dv')):
            day = addDays(monday, i)
            hours = timetable[weekday]
            workforce = sum(
                1
                for lines in hours
                for person in lines
                if person not in excluded
            )
            included.update({
                person
                for lines in hours
                for person in lines
                if person not in excluded
            })
            tsv.write(f"{day}\t{workforce}\n")


@cli.command()
@click.argument(
    'monday',
    type=Date,
)
def launch(monday):
    import requests
    from emili import sendMail 
    from tomatic.config import secrets
    import time
    import uuid

    config = ns.load('config.yaml')
    minutes = secrets('tomatic.plannerGraceTime', 2*60)

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
reenvia aquest mateix correu a incidencies ({secrets('tomatic.supportmail')}).
"""


    sendMail(
        sender=secrets('tomatic.dailystats.sender'),
        to=secrets('tomatic.dailystats.recipients'),
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

