<a href="https://www.ccma.cat/tv3/alacarta/la-meva-infantils/tomatic-club-super-3/video/4586233/">
<img
title="Tomàtic, a chatting tomato-answering machine. Until 2006, it featured on 'Club Super3', a show for kids aired by the catalan public TV. Alledgedly started to work at Som Energia in 2015."
src="doc/tomatic.jpg" align='right'
/>
</a>

[![Build Status](https://app.travis-ci.com/Som-Energia/somenergia-tomatic.svg?branch=master)](https://app.travis-ci.com/Som-Energia/somenergia-tomatic)
[![Coverage Status](https://coveralls.io/repos/github/Som-Energia/somenergia-tomatic/badge.svg?branch=master)](https://coveralls.io/github/Som-Energia/somenergia-tomatic?branch=master)

# Som Energia's Tomàtic
**The coolest companion of phone attention crew  at Som Energia**



- [Features](#features)
- [Setup](#setup)
  - [Development Setup](#development-setup)
  - [Production Setup](#production-setup)
  - [Configuration](#configuration)
  - [Setting up cron tasks](#setting-up-cron-tasks)
  - [Setting up Hangouts notification](#setting-up-hangouts-notification)
  - [Google Drive data sources](#google-drive-data-sources)
  - [PBX callerid callback](#pbx-callerid-callback)
- [Command Line Usage](#command-line-usage)
  - [Starting the web and API server](#starting-the-web-and-api-server)
  - [Updating Asterisk extensions](#updating-asterisk-extensions)
  - [Controlling Asterisk real-time queue](#controlling-asterisk-real-time-queue)
  - [Full list of CLI tools](#full-list-of-cli-tools)
- [Developers notes](#developer-notes)
  - [Developing with autoreload](#developing-with-autoreload)
  - [How to release](#how-to-release)
  - [How to upgrade your server](#how-to-upgrade-your-server)
  - [Code map](#code-map)

Other documentation

- [CHANGES.md](CHANGES.md): Version history and change log
- [CODEMAP.md](CODEMAP.md): Explains the structure of the code (first read if you start developing)
- [TODO.md](TODO.md): Task list
- [doc](docs) Further documentation


## Features

This software is used within SomEnergia cooperative to improve the quality of the phone support we give to our members and clients.

- **It distributes helpline turns among the staff**

	Each week it decides the turns each person will be attending to the phone.
	Takes into account a provided ideal load for every one, their holidays, meetings,
	and some nice restrictions to ensure **staff wellbeing** and **service quality**.

- **Manual edition of the resulting time table**

	Unscheduled meetings and other events, often makes the computed timetable outdated.
	The web interface can be used to swap turns on the timetable and keep track of the changes.

- **Programming Asterisk queues according the timetable**

	Every turn, Tomàtic automatically setups the PBX queue according to the timetable.
	It sends friendly reminders to the people on duty and
	warns the coordinators whenever an agent is not connected to the PBX
	because of technical or human memory issues.

- **Realtime control of the current queue***

	You can pause agents to adapt to temporary absences,
	or adding more agents in case of bursts of incomming calls.
	Tomatic visually shows the state of each extension in the queue:
	Available, attending a call, disconnected, paused...

- **Instant information about the incomming call**

	For each incomming call, Tomàtic retrieves all the information
	in our ERP related to that number and displays it
	to the agents in an accessible format:
	contracts, invoices, alerts, previous notes...
	this way agents can resolve calls faster and better.
	If the phone is not in the database,
	still the agent can perform searches using many criteria.

- **Integrated call annotation**

	With a few clicks you can annotate current and past calls.
	Such annotations can be used to start an official claim procedure
	or just to keeps some stats that will help to improve the quality of service.

- **Tomàtic impersonation**

	Turn team coordination messages into a smile by impersonating Tomàtic
	in the chat group. It seems an amusement feature but, keeping a smile
	in our faces makes our service also nicer.

## Setup

### Development setup

```bash
sudo apt-get install git gcc libffi-dev libssl-dev nodejs npm
git clone https://github.com/Som-Energia/somenergia-tomatic.git
cd somenergia-tomatic
npm install
npm run build # for development assets
virtualenv .venv
python setup develop
```

### Production Setup

- Install pyenv in the running user. Follow ["Basic github install"](https://github.com/pyenv/pyenv#basic-github-checkout)

```bash
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git nodejs npm
sudo mkdir -p /opt/www/somenergia-tomatic
sudo mkdir -p /var/log/somenergia/
sudo chown tomatic:tomatic /opt/www/somenergia-tomatic
sudo su tomatic # the user that will run it

git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"
pyenv install 3.9.4 --verbose
pyenv global 3.9.4
pip install -U virtualenv
cd /opt/www/somenergia-tomatic
git clone https://github.com/Som-Energia/somenergia-tomatic.git .
virtualenv .venv
source .venv/bin/activate
python setup develop
npm install
npm run deploy # for production assets
```

### Configuration

- Copy `config-example.yaml` as `config.yaml` and edit it
- Copy `dbconfig-example.py` as `dbconfig.py` and edit it
- `echo '{}' > persons.yaml`

### Setting up cron tasks

This is needed in order to enable automations including:

- programming queues in the PBX according the turns in the timetable
- hangouts notifications just before each turn
- hangouts reporting of the daily stats
- updating the extension names in the PBX

```bash
sudo chown root:root crontab
sudo chmod 755 crontab
sudo ln -s $pwd/crontab /etc/cron.d/tomatic
```

### Setting up Hangouts notification

This can be done by using the hangups application that should have been installed as dependency.
If your main environment is still Python2, you should setup a separate Python3 virtualenv to use `hangup`.
since it is not compatible with Python 2.

- Create an account for the boot in hangouts.google.com.
- Generate an access key
  ```
  $ hangups --manual-login
  ```
  The key will be stored in `~/.cache/hangups/refresh_token.txt`
- Figure out the target channel ID. You can do so by running this hangups example:
  [`build_conversation_list.py`](https://raw.githubusercontent.com/tdryer/hangups/master/examples/build_conversation_list.py)
  which requires this other file to be in the same dir:
  [`common.py`](https://raw.githubusercontent.com/tdryer/hangups/master/examples/common.py)
- Write down channel ID in `config.yaml` as `hangoutChannel`
- You can test it by running `tomatic_says.py hello world`

### Google Drive data sources

Computing timetables requires access to a Google Drive Spreadsheet
where you store the source configuration: leaves, ideal work load...
In order to access it, you must provide a certificate.
Google change the interface so often is hard to provide a set of steps.
In overall it would be:

- Create a project in https://console.developers.google.com/project
- Create a service account within the project (service email address)
- Create a credential key within the service account (will result in a json file with a key)
- Save that file as `drive-certificate.json` in the root folder of tomatic code
- Take the `client_email` key in the json file and grant that mail access to the spreadsheet

The gspread library, this is using provide a more detailed and up to date steps:
http://gspread.readthedocs.org/en/latest/oauth2.html

If you don't want to download the configuration data from the Google Drive
SpreadSheet, you can provide the `--keep` option to the commands.

Related parameters in `config.yaml` file are:

- `documentDrive`: the title of the spreadsheet, it must be accessible by the key
- `fullCarregaIdeal`: the spreadsheet sheet where the ideal shift load is stored.
- `idealLoadValuesRange`: The range name in document and sheet with the values of the ideal load values for each person
- `idealLoadValuesName`: The range name in document and sheet with the corresponding names of each person
- `leavesSheet`: The document sheet where a person off in leave appear in every row

Holidays are taken from a sheet named as the year, pe. `2020`
containing named ranges like `Vacances202Semester1`
which are tables a column for each semester day and a row per person.

### PBX callerid callback

Tomatic can auto-search of the current incomming call.
To achieve that, you must program your PBX AGI scripts to send a request to the Tomatic API.

For example, with curl, if the person with the extension 101 is going to
receive a call from 555441234:

```bash
$ curl --max-time 1 -X POST  $BASEURL/api/info/ringring --data ext=101 --data phone=555441234 || true
```

Notice the `--max-time 1` used to avoid stalling the call if the api is down.
And notice, also, the trailing `|| true` to ensure the call success.
Both may be needed, depending on how you call this from you PBX.

## Command Line Usage

### Starting the web and API server

To run the fake version to develop:

```bash
$ ./tomatic_api.py --debug --fake
# In a different terminal, for the ui
npm run start
```

To run the version acting on asterisk:

```bash
$ ./tomatic_api.py
```

Use `--help` to see other options.

### Planning time tables

Notice: Now, this can be launched from the web user interface.

To compute the timetable for the next week:

```bash
$ ./schedulehours.py
```

To skip the downloading of the data from google drive:

```bash
$ ./schedulehours.py --keep
```

See bellow how to grant access to the script.

### Updating Asterisk extensions

Tomatic can load all persons extension numbers from its configuration to Asterisk.
Be careful, those changes might cut ongoing communications.
A cron task performs it weekly every friday afternoon when all communications are over.
You can force it yourself by running:

```bash
$ ./tomatic_extension.py load
```
To see which extensions are configured

```bash
$ ./tomatic_extension.py show
```

### Controlling Asterisk real-time queue

Normally this is operated from the crontab and from the Tomatic's user interface.
But you can also use this script from the server to perform several non-anticipated operations.

To load the current answering queue acording to the schedule
```bash
$ ./tomatic_rtqueue.py set
```

To load the queue of a different time (for testing purposes):
```bash
$ ./tomatic_rtqueue.py set -d 2018-12-26 -t 10:23
```
To see the current queue (besides Tomatic web interface)

```bash
$ ./tomatic_rtqueue.py show
```
The script offer other commands to add users, pause and resume them and clear the queue.
Feel free to read the help:

```bash
$ ./tomatic_rtqueue.py --help
```

## Full list of CLI tools

Thats the full list of CLI tools.
Most of them have their own `--help` to know how to use them:

### Main scripts

- `tomatic_api.py`: Launches the web and API.
- `tomatic_says.py`: Impersonates Tomatic on hangouts.

### Callinfo related

- `tomatic_callinfo.py`: Retrieves client info by several criteria
- `create_atc_case.py`: Uploads daily CRM cases to the ERP

### Pbx related

- `tomatic_rtqueue.py`: Controls the agents currently receiving calls
- `tomatic_extensions.py`: Controls agent's extensions
- `tomatic_calls.py`: Retrieves call stats from the PBX (not supported by current areavoip pbx)
- `areavoip_dailyreport.py`: Generates the daily call report (from areavoip PBX)
- `areavoip_callapi.py`: Calls from CLI arbitrary operation of the areavoip PBX API

### Timetable computation related

- `tomatic_busy.py`: Ops with people's availability (to spot critical days and so on)
- `tomatic_retrieve.py`: Call different data retrievals by CLI (holidays, leaves, persons, idealshifts...)
- `tomatic_mergeshifts.py`: Merge operations with shift load files (dicts person to number)
- `tomatic_resetshiftcredit.sh`: Clears the debts and credits of shifts
- `tomatic_shiftload.py`: Computes person's shift load for the week. Prior step to compute a timetable.
- `tomatic_scheduler.py`: Computes timetables.
- `tomatic_uploadtimetable.py`: Uploads timetables to the API.

### Crontab and scriptlauncher

- `runhere`: Wrapper to simplify script usage from crontab and scriptlauncher. Sets the cwd and the virtual env.
- `scriptlauncher.yaml`: [Scriptlauncher](http://github.com/som-energia/scriptlauncher) configuration to add Tomatic related scripts.
- `crontab`: crontab file to be linked to /etc/cron.d/, see [Setting up cron tasks](#setting-up-cron-tasks)
- `crontab-dailyreport.sh`: Sends the dailyreport at the end of the day
- `crontab-warnturn.sh`: Warns operators for the next turn


# Developers notes

## Developing with autoreload 

```bash
# in different terminals
npm run start
./tomatic_api.py --debug --fake
```

The `--fake` option enables a fake pbx to avoid messing with the actual one.
You might setup a testing queue and use the `--queue` option instead.


## How to release

- Change version number in
	- `package.json`
	- `tomatic/__init__.py`
- Add versions changes to `CHANGES.md`
- Commit
- `git tag tomatic-M.m.r` (Major minor release)
- `git push`
- `git push --tags`


## How to upgrade your server

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





