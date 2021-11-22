# Developing Tomàtic

This page explains topics relevant just to developers
hacking Tomàtic.

- [Autoreload setup](#autoreload-mode)
- [Release process](#release-process)
- [Upgrading servers](#upgrading-servers)
- [Code map](#code-map)
- [Files](#files)

## Auto-Reload mode

For development autoreload setup is recommended, for both frontend and backend.

```bash
# in different terminals
npm run start
scripts/tomatic_api.py --debug --fake
```

The `--fake` option enables a fake pbx to avoid messing with the actual one.
You might setup a testing queue and use the `--queue` option instead.


## Release process

- Change version number in
	- `package.json`
	- `tomatic/__init__.py`
- Add versions changes to `CHANGES.md`
- Commit
- `git tag tomatic-M.m.r` (Major minor release)
- `git push`
- `git push --tags`


## Upgrading servers

Warning: This might be kind of specific for Som Energia's setup
because of the paths and the usage of supervisorctl.

```bash
cd /opt/www/somenergia-tomatic # Or wherever you installed it
git fetch
git rebase
# Rebase changes the properties of crontab file
sudo chown root:root crontab
sudo chmod 755 crontab
# Npm commands just if the release modified the js part
npm install
npm run build # for development assets
npm run deploy # for production assets
# Then upgrading the python part
source .venv/bin/activate
pip install -e .
# Restart the application
sudo supervisorctl restart tomatic
```

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

- `asteriskfake.py`: A fake implementation of a pbx to be controlled
- `asteriskcli.py`: Partial pbx controller implementation using asterisk CLI thru ssh (complements dbasterisk)
- `dbasterisk.py`: A pbx controller using the realtime Asterisk DB
- `pbxareavoip.py`: A pbx controller using areavoip API
- `pbxqueue.py`: Pbx controller wrapper to assume the same queue on construction

### Tools

- `execution.py`: Encapsulates an asynchronous execution of a sandboxed process (used by `planner_api.py`)
- `remote.py`: Simplifies remote process execution and access to files via SSH
- `directmessage`: modules that abstract actual direct message (hangouts or equivalents)
- `directmessage/hangouts`: Google hangouts implementation of directmessage

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

### CRM

- `callinfo.py`: Retrieves incomming call information from the ERP
- `callregistry.py`: Call logging and annotation
- `claims.py`: Access the ERP's Claim objects (Backend of callregistry)


## Files

This is a review of the callinfo files.

- `call_log`:
	- "registre de trucades (reclamació i no reclamacio)"
	- `callinfo/dailycalls.yaml`
	- `config.my_calls_log`
	- person dict to a list of incomming calls of the day
- `info_call_types`:
	- "tipus de motius no reclamacio"
	- `callinfo/info_types.txt`
	- `config.info_cases`
	- a line for each type description
	- Venen d'un drive de la comi de telefon
- `claim_types`:
	- "tipus de reclamacions"
	- `callinfo/claim_types.txt`
	- `config.claims_file`
	- A line for each type of claim
- `claim_types_keywords`:
	- "paraules clau dels tipus de motius reclamacio"
	- `callinfo/claims_dict.yaml`
	- `config.claims_dict_file`
	- dictionary classificacio dels motius


Atc Cases: Formal claims
Info Cases: The rest of calls not a claim



