# somenergia-tomatic

[![Build Status](https://travis-ci.org/Som-Energia/somenergia-tomatic.svg?branch=master)](https://travis-ci.org/Som-Energia/somenergia-tomatic)
[![Coverage Status](https://coveralls.io/repos/github/Som-Energia/somenergia-tomatic/badge.svg?branch=master)](https://coveralls.io/github/Som-Energia/somenergia-tomatic?branch=master)

Somenergia Phone Support Helper

This software is used within SomEnergia cooperative to manage phone support to members and clients.

- Distributes helpline shifts among the staff.

	Given the ideal load and availability for everyone, and some restrictions
	to ensure staff wellbeing and service quality,
	it decides each week a timetable each person must be attending the phone.

- Manual edition of the resulting time table

	Often unscheduled meetings and other issues makes the computed timetable unpractical.
	The web interface can be used to swap turns and keep track of the changes.

- Programming Asterisk queues according the timetable.

	Asterisk queue is reload for each turn automatically.

- Pause/Resume extensions or adding more lines during service

	In order to adapt to incoming call and temporary unavailabilities,
	you can pause or resume lines in the running queue or adding
	new lines.

- Incomming call info

	For each incomming call agents get a refreshed view of the ERP
	information related to that number: contracts, invoices, alerts,
	previous notes... this way agents can resolve calls faster and better.


## Setup

### Dependencies and assets building

- Install pyenv in the running user. Follow ["Basic githup install"](https://github.com/pyenv/pyenv#basic-github-checkout)

```bash
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git nodejs npm
sudo mkdir -p /opt/www/somenergia-tomatic
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
npm run build # for development assets
#npm run deploy # for production assets # TODO failing
```

Development setup

```bash
sudo apt-get install git gcc libffi-dev libssl-dev nodejs npm
git clone https://github.com/Som-Energia/somenergia-tomatic.git
cd somenergia-tomatic
npm install
npm run build # for development assets
npm run deploy # for production assets
virtualenv .venv
python setup develop
```

### Configuration

- Copy `config-example.yaml` as `config.yaml` and edit it
- Copy `dbconfig-example.py` as `dbconfig.py` and edit it
- `echo '{}' > persons.yaml`

### Setting up cron tasks

This is needed in order to enable automatic asterisk shift switching
and hangouts notifications.

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

## Google Drive data sources

Computing timetables requires access to a Google Drive Spreadsheet
where you store the source configuration: vacations, leaves, ideal work load...
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

### Callerid API for PBX callback

In order for Callinfo page to update whenever you receive a call,
the PBX should send a POST to the `/api/info/ringring` API entrypoint.
The postdata should contain two variables `phone` and `ext`
containing the caller id and the receiving extension.

For example, with curl:

```bash
$ curl -X POST  $BASEURL/api/info/ringring --data ext=101 --data phone=555441234
```

## Usage

### Scheduler

To compute the timetable for the next week:

```bash
$ ./schedulehours.py
```

To skip the downloading of the data from google drive:

```bash
$ ./schedulehours.py --keep
```

See bellow how to grant access to the script.

### Web and API

To run the fake version to develop:

```bash
$ ./tomatic_api.py --debug --fake
```

To run the version acting on asterisk:

```bash
$ ./tomatic_api.py
```

Use `--help` to see other options.

### Direct asterisk extension configuration

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

### Direct asterisk rtqueue control

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



# Developers notes

## How to release

- Change version number in
	- `package.json`
	- `tomatic/__init__.py`
- Add versions changes to `CHANGES.md`
- Commit
- `git tag tomatic-M.m.r` (Major minor release)
- `git push`
- `git push --tags`


## How to deploy upgrades (specific for Som Energia's deployment)

```bash
git fetch
git rebase
# Rebase changes the properties of crontab file
sudo chown root:root crontab
sudo chmod 755 crontab
# Npm commands just if the release modified the js part
npm install
npm run build # for development assets
npm run deploy # for production assets
sudo pip install -e .
sudo supervisorctl restart tomatic
```

# Code map

## API

- `api.py`: Main Flask application, includes
	- Person management API
	- Busy management API
	- Timetable editing API
	- PBX state control API
	- Callinfo (CRM) API
- `planner_api.py`: Flask blueprint to launch timetable schedulers in background
- `execution_api.py`: Flask blueprint using execution.py to launch arbitrary commands (not mounted just to test execution infrastructure)

## PBX control

- `asteriskfake.py`: A fake implementation of a pbx to be controlled
- `asteriskcli.py`: Partial pbx controller implementation using asterisk CLI thru ssh (complements dbasterisk)
- `dbasterisk.py`: A pbx controller using the realtime Asterisk DB
- `pbxareavoip.py`: A pbx controller using areavoip API
- `pbxqueue.py`: Pbx controller wrapper to assume the same queue on construction

## Tools

- `execution.py`: Encapsulates an asynchronous execution of a sandboxed process (used by `planner_api.py`)
- `remote.py`: Simplifies remote process execution and access to files via SSH
- `directmessage`: modules that abstract actual direct message (hangouts or equivalents)
- `directmessage/hangouts`: Google hangouts implementation of directmessage

## Information Access

- `retriever.py`: Encapsulates access to data sources (API's, drive documents...)
- `busy.py`: Encapsulates person availability information
- `persons.py`: Encapsulates person profiles (name, extension, email, color, groups, table...)
- `schedulestorage.py`: Encapsulates the timetables directory
- `scheduling.py`: Encapsulates access to timetable structure (yaml)
- `htmlgen.py`: Generates a timetable html, old code, a template would do

## Timetable generation

- `shiftload.py`: Compute how many shifts each person has to do weekly
- `backtracker.py`: The main timetable solver

## CRM

- `callinfo.py`: Retrieves incomming call information from the ERP



# Files

This is a review of the callinfo files.

- `info_call_log`:
	- "registre de motius no reclamació"
	- `info_cases/YYYYMMDD.yaml`
	- person dict to a list of info cases
	- voki: removed
- `claim_log`:
	- "registre de motius reclamació"
	 `atc_cases/YYYYMMDD.yaml`
	- person dict to a list of atc cases (in ordre to create claims in the ERP)
	- voki: removed
- `call_log`:
	- "registre de trucades (reclamació i no reclamacio)"
	- `atc_cases/today_calls.yaml`
	- `config.my_calls_log`
	- person dict to a list of incomming calls of the day
	- voki: renamed in config as `callinfo/dailycalls.yaml`
- `info_call_types`:
	- "tipus de motius no reclamacio"
	- `callinfo/info_cases.yaml`
	- `config.info_cases`
	- NOT A YAML!
	- a line for each type description
	- Venen d'un drive de la comi de telefon
	- voki: renamed in config as `callinfo/info_types.txt`
- `claim_types_keywords`:
	- "paraules clau dels tipus de motius reclamacio"
	- `claims_dict.yaml`
	- `config.claims_dict_file`
	- dictionary classificacio dels motius
	- voki: renamed in config as `callinfo/claims_dict.yaml`
- `claim_types`:
	- "tipus de reclamacions"
	- `claims.yaml`
	- `config.claims_file`
	- NOT A YAML!
	- A line for each type of claim
	- voki: renamed in config as `callinfo/claim_types.txt`


Atc Cases: Formal claims
Info Cases: The rest of calls not a claim



# TODO's

- GSpread docs say that moving the credential to `~/.config/gspread/service_account.json` avoids having to pass it around as parameter
- CallInfo
	- [ ] /api/getInfos -> /api/call/infotypes
	- [ ] Pujar infos a l'ERP
	- [ ] Commit `info_cases/info_cases.yaml`
	- [ ] Commit `claims_dict.yaml`
	- [ ] /api/updateClaims -> /api/call/claimtypes/update
	- [ ] /api/getClaims -> /api/call/claimtypes
	- [ ] /api/updatelog/<ext> -> /api/call/log/<ext>
	- [ ] /api/personlog without <ext> has no sense, remove it
	- [ ] /api/personlog/<ext> en els casos de fallada returnar una llista buida sense errors (no son de fallada, encara no hi ha logs i prou)
	- [ ] /api/personlog/<ext> /api/call/log/<ext>
	- [ ] /api/api/log Deprecated
	- [ ] components/call.js:getLog Deprecrated
	- [ ] /api/claimReasons Deprecated (no ui code aparently)
	- [ ] /api/infoReasons Deprecated (no ui code aparently)
	- [ ] /api/callReasons Deprecated (no ui code aparently)
	- [ ] Revisar handshaking dels websockets
	- [ ] /api/info/ringring -> /api/call/ringring
	- [ ] Fer la data ISO al call_log
	- [ ] /api/info/all/<field> -> /api/info/by/any/<value>
	- [ ] /api/info/xxxx/<field> -> /api/info/by/xxxx/<value>
	- [ ] Refactoritzar codi comu dels getInfoPersonByXXXX


- Refactoring
	- [x] use persons interface everywhere
		- [x] api uses persons
			- [x] persons() set attributes with ns() if not found
			- [x] persons.update(person, **kwds)
		- [ ] scheduler use persons
		- [ ] tomatic_says use persons
		- [ ] tomatic_calls uses persons
		- [ ] shiftload uses persons
	- [x] use pbx backends instead of current pbx interface
		- [x] remove use setScheduledQueue (mostly in tests)
		- [x] unify backend interfaces
		- [x] dbasterisk works with names not extensions

- Hangout
	- [x] Configurable token file path
	- [x] Choose output channel by CLI
	- [x] Choose token file by CLI
	- [x] List channels when no channel has been configured yet
- Planner:
	- [ ] Refactor as Single Page App
	- [ ] Style it
	- [ ] Show cutting reasons of best solutions
	- [ ] Ask before deleting, killing, uploading...
- Scheduler:
	- [ ] Join load computation into the script
- Person editor:
	- [ ] Disable ok until all fields are valid
	- [ ] Check extension not taken already
	- [ ] Focus on first item
	- [ ] Take person info from holidays manager
- Callinfo
	- [ ] Simplify yaml structure
	- [ ] Refactor tests
	- Alerts:
		- [ ] Unpaid invoices





