# somenergia-tomatic

[![Build Status](https://travis-ci.org/Som-Energia/somenergia-tomatic.svg?branch=master)](https://travis-ci.org/Som-Energia/somenergia-tomatic)
[![Coverage Status](https://coveralls.io/repos/github/Som-Energia/somenergia-tomatic/badge.svg?branch=master)](https://coveralls.io/github/Som-Energia/somenergia-tomatic?branch=master)

Somenergia Phone Support Helper

This software is used within SomEnergia cooperative to manage phone support to members and clients.

- Distributes turns among the staff.

	Given the ideal load and availability for everyone, and some restrictions
	to ensure staff wellbeing and service quality,
	it decides each week a timetable each person must be attending the phone.

- Manual edition of the resulting time table

	Often unscheduled meetings and other issues makes the computed timetable unpractical.
	The web interface can be used to swap turns and keep track of the changes.

- Asterisk queues programming according the timetable.

	Each turn, the Asterisk queue is reloaded in order to meet the timetable.

- Pause/Resume extensions or adding more lines during service

	In order to adapt to incoming call and temporary unavailabilities,
	you can pause or resume lines in the running queue or adding
	new lines.

- Incomming call info

	Call id is used to retrieve information from the ERP useful
	for resolving calls faster and better.



## Setup

### Dependencies and assets building

```bash
sudo apt-get install gcc libpython2.7-dev libffi-dev libssl-dev nodejs-legacy npm
python setup develop
npm install
npm run build # for development assets
npm run deploy # for production assets
```

### Setting up cron tasks

This is needed in order to enable automatic asterisk turn switching
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

### Google Drive data sources

In order  to compute personal load,
scheduler requires some input data to be taken from
a Google Drive Spreadsheet document.
You might also use `--keep` option to relay in local files instead,

In order to access it you will require a oauth2 certificate and to grant it
access to the Document.

Follow instructions in http://gspread.readthedocs.org/en/latest/oauth2.html

You can skip steps 5 (already in installation section in this document) and
step 6 (code related) but **don't skip step 7**.

Create a link named 'certificate.json' pointing to the actual certificate.

Related parameters in `config.yaml` file are:

- `documentDrive`: the title of the spreadsheet, it must be accessible by the key
- `fullCarregaIdeal`: the spreadsheet sheet where the ideal shift load is stored.
- `idealLoadValuesRange`: The range name in document and sheet with the values of the ideal load values for each person
- `idealLoadValuesName`: The range name in document and sheet with the corresponding names of each person
- `leavesSheet`: The document sheet where a person off in leave appear in every row

Holidays are taken from a sheet named as the year, pe. `2020`
containing named ranges like `Vacances202Semester1`
which are tables a column for each semester day and a row per person.



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




## Deployment notes

In order to access the configuration available in the Google Drive SpreadSheet
you must provide a 

- Create a Google Apps credential:
    - Create a project in https://console.developers.google.com/project
    - Go to “Credentials” and hit “Create new Client ID”.
    - Select “Service account”. Hitting “Create Client ID” will generate a new
      Public/Private key pair.
    - Download and save it as 'credential.json' in the same folder the script is
    - Take the `client_email` key in the json file and grant it access to the
      'Vacances' file as it was a google user

If you don't want to download the configuration data from the Google Drive
SpreadSheet, you can provide the `--keep` option.


# Developers notes

## How to release

- Change version number in
	- `package.json`
	- `tomatic/__init__.py`
- Add versions changes to `CHANGES.md`
- Commit
- `git tag tomatic-M.m.r` Major minor release
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


# TODO's

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





