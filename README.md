# somenergia-tomatic

[![Build Status](https://travis-ci.org/Som-Energia/somenergia-tomatic.svg?branch=master)](https://travis-ci.org/Som-Energia/somenergia-tomatic)

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



## Install


```bash
sudo apt-get install gcc libpython2.7-dev libffi-dev libssl-dev nodejs-legacy npm
python setup develop
npm install
npm run build # for development assets
npm run deploy # for production assets
```

See below "deployment notes" on how deploy the required certificate.


### Cron

This is needed in order to enable automatic asterisk turn switch
and hangouts notification.

```bash
sudo chown root:root crontab
sudo chmod 755 crontab
sudo ln -s $pwd/crontab /etc/cron.d/tomatic
```

You should run first, at least once, `tomatic_says.py` to get asked for Hangouts authentification.


## Configuration


### `config.yaml`

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


## Certificates

Unless you specify the `--keep` option, required configuration data is
downloaded from the Google Drive spreadsheet where phone load, holidays and
availability are written down.

In order to access it you will require a oauth2 certificate and to grant it
access to the Document.

Follow instructions in http://gspread.readthedocs.org/en/latest/oauth2.html

You can skip steps 5 (already in installation section in this document) and
step 6 (code related) but **don't skip step 7**.

Create a link named 'certificate.json' pointing to the actual certificate.





# TODO's


- Scheduler:
	- [x] Do not read busy entries from gdrive, just holidays and load
- Page:
	- [x] Quitar segundo return del Panel
	- [x] Header funcionando en Chrome
- Busy:
	- [x] Disable ok until all fields are valid
	- [x] If cancel remove items
	- [x] Poner el nombre de personas en el dialogo
	- [x] Save changes as they are done
	- [x] Reason field not clear a field
	- [x] Revisar default date next monday
	- Validate one turn selected
	- Mejorar el selector de fecha
	- ESC en el busy entry editor cierra los dos dialogos
	- Sort busy entries on file
	- Filter out old oneshot entries
	- Focus on first item
- Person:
	- Disable ok until all fields are valid
	- Check extension not taken already
	- Focus on first item
- Move config data to its own private repo
- Commit interactive changes to config files
- Callinfo
	- Simplify yaml structure
	- Refactor tests
	- [x] Link in a new window to helpscout last emails
	- Missing field:
		- [x] contract number
		- [x] contract address
		- [x] contract persons (payer, owner, host)
			- [x] Email and helpscout link
			- [x] DNI
			- Phone
	- Alerts:
		- [x] Delayed invoicing
		- [x] Pending or recent ATR cases
		- Unpaid invoices





