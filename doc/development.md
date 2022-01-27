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
- Commit "bump to M.m.r"
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

## Smoke tests

(Som Energia specific, you could adapt them)

What smoke tests you should be doing after an upgrade to check most components should be up and running:

- Go to http://tomatic.somenergia.lan and check it shows the production pbx queue, modify the queue (ie, add yourself and pause)
- Go to http://ketchup.somenergia.lan and check it works the testing pbx queue, should be different than production, modify it
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

- `callinfo/categories.yaml`
	- Categories to choose when annotating calls
	- It also contains the sections to choose when the category has no predefined one in the ERP
	- The list is built from the ERP when /api/call/categories/update
	- Each category has `code`, `name`, `isClaim`, `section`
- `callinfo/dailycalls.yaml`
	- "registre de trucades (reclamació i no reclamacio)"
	- `config.my_calls_log`
	- person dict to a list of incomming calls of the day



