# Tomàtic Command Line Tools

Tomàtic comes with many command line tools.
Most of them come with a proper command line help (`--help`),
but it is hard which is the one you need to use.

This page includes a descriptive listing of such scripts.
Follows usage example for some of them.

- [Full list of CLI tools](#full-list-of-cli-tools)
- [Starting the web and API server](#starting-the-web-and-api-server)
- [Updating Asterisk extensions](#updating-asterisk-extensions)
- [Controlling Asterisk real-time queue](#controlling-asterisk-real-time-queue)

## Full list of CLI tools

Thats the full list of CLI tools.
Most of them have their own `--help` to know how to use them:

### Main scripts

- `tomatic_api.py`: Launches the web and API.
- `tomatic_says.py`: Impersonates Tomatic on hangouts.

### CRM/Callinfo related

- `tomatic_callinfo.py`: Retrieves client info by several criteria
- `create_atc_case.py`: Uploads daily CRM cases to the ERP

### PBX/Asterisk related

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
- `crontab`: crontab file to be linked to /etc/cron.d/, see [Setting up cron tasks](setup.md#setting-up-cron-tasks)
- `crontab-dailyreport.sh`: Sends the dailyreport at the end of the day
- `crontab-warnturn.sh`: Warns operators for the next turn



## Starting the web and API server

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

## Planning time tables

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
## Updating Asterisk extensions

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



