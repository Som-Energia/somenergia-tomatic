# Developing Tomàtic

This page explains topics relevant just to developers
hacking Tomàtic.

- [Context](#context)
- [Autoreload setup](#autoreload-mode)
- [Release process](#release-process)
- [Upgrading servers](#upgrading-servers)
- [Code map](#code-map)
- [Files](#files)

## Context

See [Context diagram and explication](architecture-context.md)
to get a summary of the persons and systems
Tomatic interacts with.

## Setup

See [Setup](setup.md)

## Auto-Reload mode

For development autoreload setup is recommended, for both frontend and backend.

```bash
# in different terminals
npm run start
scripts/tomatic_api.py --debug --fake
```

The `--fake` option enables a fake pbx to avoid messing with the actual one.
You might setup a testing queue and use the `--queue` option instead.

IMPORTANT: Since the migration to FastAPI,
`tomatic_api` options `--fake`, `--pbx` and `--queue` do not work.
Instead you can set the equivalent options in `dbconfig.py`
until the [https://github.com/Som-Energia/somenergia-tomatic/issues/19](issue) is solved.

## Release process

- Change version number in
	- `package.json`
	- `tomatic/__init__.py`
- Add versions changes to `CHANGES.md`
    - Specify any configuration, deployment changes... as "Upgrade Notes" for the version
- Commit "bump to M.m.r"
- `git tag tomatic-M.m.r` (Major minor release)
- `git push`
- `git push --tags`


## Upgrading servers

Warning: This might be kind of specific for Som Energia's setup
because of the paths and the usage of supervisorctl.

```bash
# First review any "Upgrade Notes" in `CHANGES.md` for the last versions
cd /opt/www/somenergia-tomatic # Or wherever you installed it
git fetch
git rebase
# Rebase changes the properties of crontab file
sudo chown root:root crontab
sudo chmod 755 crontab
# Frontend deployment
npm install
npm run build # for development assets
npm run deploy # for production assets
# Backend deployment
source .venv/bin/activate
pip install -e .
# Restart the application
sudo supervisorctl restart tomatic
```

## Smoke tests

(Som Energia specific, you could adapt them)

What smoke tests you should be doing after an upgrade to check most components should be up and running:

- Go to http://tomatic.somenergia.coop and check it shows the production pbx queue, modify the queue (ie, add yourself and pause)
- Go to http://pebrotic.somenergia.coop and check it works the testing pbx queue, should be different than production, modify it
- Go to http://tomatic.somenergia.lan:5000 and check scriptlauncher, use an script, ie, reset the queue, to reset former changes to the queues
- Check tomatic says from scriptlauncher with you email as a target (certificates and api versions problems might trigger)
- Login as one of the operators and check callinfo shows the former calls, click one that triggers a search
- Go to the scriptlauncher and launch a shift load (will trigger any problems on downloading required data: odoo, drive connections...)
- Go to the planner and launch a timetable (will trigger any problems on downloading required data: odoo, drive connections...). Delete the task to avoid messing AiS team.
- As root (to keep userid and perms), uncomment the testing crontab line to check crontab is fine and working 

## Code map

### API

- `api.py`: Main FastAPI application, includes
	- Person management API
	- Busy management API
	- Timetable editing API
	- PBX state control API
	- Callinfo (CRM) API
- `planner_api.py`: Sub API to launch timetable schedulers in background
- `execution_api.py`: Sub API using execution.py to launch arbitrary commands (not mounted just to test execution infrastructure)

### PBX control

- `pbx/__init__.py`: Implementation neutral factory to the many pbx interface implementations
- `pbx/asteriskfake.py`: A fake implementation of a pbx to be controlled
- `pbx/asteriskcli.py`: Partial pbx controller implementation using asterisk CLI thru ssh (complements dbasterisk)
- `pbx/dbasterisk.py`: A pbx controller using the realtime Asterisk DB
- `pbx/pbxareavoip.py`: A pbx controller using areavoip API
- `pbx/pbxirontec.py`: A pbx controller using irontec API
- `pbx/pbxqueue.py`: Pbx controller wrapper to assume the same queue on construction

### Tools

- `execution.py`: Encapsulates an asynchronous execution of a sandboxed process (used by `plannerexecution.py`)
- `remote.py`: Simplifies remote process execution and access to files via SSH
- `directmessage`: modules that abstract actual direct message (hangouts or equivalents)
- `directmessage/hangouts.py`: Google hangouts implementation of directmessage
- `backchannel.py`: Abstracting server initiated comunication with the clients (Websocket or equivalent)

### Information Access

- `retriever.py`: Encapsulates access to data sources (API's, drive documents...)
- `busy.py`: Encapsulates person availability information
- `persons.py`: Encapsulates person profiles (name, extension, email, color, groups, table...)
- `schedulestorage.py`: Encapsulates the timetables directory
- `scheduling.py`: Encapsulates access to timetable structure (yaml)
- `htmlgen.py`: Generates a timetable html, old code, a template would do

### Timetable generation

- `shiftload.py`: Compute how many shifts each person has to do weekly
- `backtracker.py`: The main timetable solver
- `minizinc.py`: Minizinc based timetable solver
- `plannerexecution.py`: Encapsulates an asynchronous execution of a sandboxed timetable planner (used by `planner_api.py`)

### CRM

- `callinfo.py`: Retrieves incomming call information from the ERP
- `callregistry.py`: Call logging and annotation
- `claims.py`: Access the ERP's Claim objects (Backend of callregistry)

### UI

- `dist` contains the generated javscript bundles that will be served
- `ui/` javascript code for the user interface


## Timetable Data Files

config.yaml
persons.yaml
drive-certificate.json

idealshifts.yaml
shiftcredit.yaml

graella-telefons-2022-08-01.html
graella-telefons-2022-08-01.yaml
pid
output.txt
status.yaml
taula.html


- Indisponibilitats:
    - `oneshot.conf`
	- downloaded as `/api/busy/download/oneshot`
    - `indisponibilitats.conf`
        - downloaded as `/api/busy/download/weekly`
    - `indisponibilitats-vacances.conf`
    - `holidays.conf`
    - `leaves.conf`

- Credit
    - `graelles/shiftcredit-YYYY-MM-DD.yaml`
	- downloaded and processed with others as `/api/shifts/download/credit/YYYY-MM-DD`
	- by downloadShiftCredit() which stores it as `shiftcredit.yaml`

- shiftcredit.yaml
    - loaded by ShiftLoadComputer.loadData()

To be removed?

- `carrega.csv`
- `carrega-YYYY-MM-DD.yaml`
- `carrega-YYYY-MM-DD.csv`
    - downloaded as `/api/shifts/download/shiftload/YYYY-MM-DD`
    - retreieved by `retriever.downloadShiftload` and saved as `config.weekShifts`
- `overload-YYYY-MM-DD.yaml`
    - generated by ShiftLoadComputer.outputResults()
        - es pot canviar el nom amb args.overload
    - downloaded as `/api/shifts/download/overload/YYYY-MM-DD`
    - retrieved by `retriever.downloadOverload` and saved into `config.overloadfile`
    - saved as config.overloadfile overwriten value (not taken from config
	- que es arg.overload
	- sino un altre cop overload-YYYY-MM-DD.yaml
    - es carrega per ficar-ho dins del yaml de la graella
    - **Proposal:** since now each execution has a sandbox, rename it as overload.yaml
- `ponderatedideal-YYYY-MM-DD.yaml
    - output for debugging only


## Callinfo Data Files

Callinfo data directory is `callinfo/` by default
but can be configured using `callinfoPath` in `config.yaml`.

- `callinfo/categories.yaml`
	- Categories to choose when annotating calls
	- It also contains the sections to choose when the category has no predefined one in the ERP
	- The list is built from the ERP when /api/call/categories/update
	- Each category has `code`, `name`, `isClaim`, `section`
- `callinfo/dailycalls/calls-NAME.yaml`
	- "registre de trucades (reclamació i no reclamacio)"
	- a list of the last calls received by NAME
- `callinfo/cases/YYYY-MM-DD.yaml` Daily call log

## Scheduler Data Files

TODO: Document which files are readed, which ones are generated and how configuration and commandline affects them


