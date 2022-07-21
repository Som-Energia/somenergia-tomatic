# Changelog

## 4.6.2 2022-07-21

- Queue Monitor: fix: not forcing black text on items
- Queue Monitor: fix: split name and extension in two lines

## 4.6.1 2022-07-19

- Fix: dailycalls were not limited to 20 per user
- Now dailycalls are split by user, to speed up api calls
- Fix: some labels didn't notice that their input had focus
- Fix: menu icon buttons were taller
- Fix: Busy dialog allowed not introducing a date or no turn
- Fix: Using native date picker in modern browsers
- Most UI components turned into modules, using emotion to avoid css conflicts
- Removed load generator menu entry since it won't be used anymore
- Internal: Uses babel and emotion
- Internal: Components extracted as modules

- Update notes:
  - npm install required (emotion and babel dependencies)
  - config.yaml `callinfoPath` should point to the parent of current `my_calls_log`.
    If not specified it will be `callinfo` by default (relative to the working path).
  - config.yaml: `my_calls_log` should be removed
  - day
  - `callinfo/dailycalls.yaml` not used anymore,
     now `callinfo/dailycalls/calls-[user].yaml is used

## 4.6.0 2022-07-12

- Stats mails shows the seconds also in 00:00:00 format
- Scheduler:
  - Load computation inside scheduler
  - If achieved load is not enough nobody/ningu is added
  - Made nobody/ningu flexible to add (not a regular person)

## 4.5.7 2022-06-02

- Fix: clicking on tabs made them disappear

## 4.5.6 2022-05-14

- timetable and load launchers use the same number of lines by default
- Fix: stats: be resilient to calls not having queuename
- Redesigned stats mail to be more clear on each figure

## 4.5.5 2022-05-23

Post new provider fixes

- Call stats: Fix: properly filtering inbound calls in irontec
- Call stats: Fix: hard limit to 10 calls moved to 10,000 
- Call stats: added bouncedcalls: calls bounced because the queue size
- Call stats: added testcalls: calls arriving to a different platform/queue

## 4.5.4 2022-05-13

- areavoip: FIX: output calls were counted as incomming
- dailystats: FIX: removed spourios quote in mail message

## 4.5.3 2022-05-10

- irontec: calls filtered by did's instead of queue
- irontec: stats added latecalls and earlycalls
- `tomatic_retrieve` works with commands to choose the retrieved info
- Fix: wrong extension called in cron
- Logger entrypoint to log user events in order to instrument usage
- gha: Added rust dependency because of cryptography package
- Packaging fixes for last setuptools
- pytest as test runner instead of nose
- late and early calls in the daily report mail

## 4.5.2 2022-04-05

- `areavoip_dumpstats`:
  - Fix: `--nodump` option was ignored
  - Instaled with setup.py
- pbxareavoip: better error reporting


## 4.5.1 2022-03-31

- Fix: areavoip stats were missing a lot of calls, using a different entry point
- Instrumentation to know who uses callinfo
- Removed wavefile dependency
- `tomatic_uploadcases` shows the number of uploaded cases
- Env `TOMATIC_DEBUG_PBX` to enable PBX traces
- `areavoip_dumpstats`: dumps historical call registry


## 4.5.0 2022-02-08

- login: Contrast colors persons buttons
- callinfo categories: button to filter claims or helpdesk categories
- callinfo categories: hide category code
- callinfo categories: hide section for helpdesk categories
- dailyreport also reports stats by chat
- irontec: implementation of the stats functionality
- new cli commands:
  - `tomatic_rtqueue.py stats` to get the daily stats
  - `tomatic_rtqueue.py calls` to get the raw daily call details

## 4.4.2 2022-01-28

- Fix: Callinfo: A second search on a call lost the relation with the selected call
- Fix: Callinfo: On successful annotation, search results were kept, now are cleared
- Fix: Callinfo: Case status was always set to open, just 'unresolved' should be.
- Fix: Callinfo: (visual) Search criteria was styled light in kumato
- Fix: PersonEditor: (visual) Table select not visible in kumato

## 4.4.1 2022-01-27

- Avoid repeated erp queries for category list by caching it into `callinfo/categories.yaml`
- Added menu option to force category list update
- /api/call/topics -> /api/call/categories
- /api/call/topics/update -> /api/call/categories/update
- Old claim/info/extra duality code cleanup
  - Removed entry points:
    - /api/updateClaims
    - /api/updateCrmCategories
    - /api/getClaims
    - /api/getInfos
  - Removed data files and their config params:
    - `claims_file` usually `callinfo/claim_types.txt`
    - `claims_dict_file` usually `callinfo/claims_dict.yaml`
    - `info_cases` usually `callinfo/info_types.txt`

## 4.4.0 2022-01-27

- Call annotation workflow redesign
  - Claims and infos unified, single log, api entry, topic list...
  - Structured info on topics/categories are retrieved
    from api avoiding fragile parsing of the description
  - Save Annotation without call, person or contract
  - `tomatic_uploadcases.py` upload both info and claims
  - All categories have a code and optionally a section
  - Translate HelpDesk section as CONSULTA
  - Translate 
  - ERP user is set on cases
- Custom banners for pebrotic and ketchup variants by CLI
- Fix: search values trimmed and urlencoded

## 4.3.2 2022-01-21

- Persistent kumato mode using local browser storage
- Monitor disconnected just after changing the shift
- Increase disconnected agents monitoring frequency

## 4.3.1 2022-01-11

- Irontec: implement queue management
- Irontec: Fix: default queues not hardcoded cli tools
- Irontec: Fix: cli forced int queue

## 4.3.0 2022-01-10

- First version Irontec PBX Backend
- PBX backend generalization and plugability
  - PBX backend factory
  - Add dbconfig.tomatic.pbx option to choose the default PBX
  - `--backend` option for all PBX related CLI tools
- Daily stats mail now include a csv file with the historical data

## 4.2.5 2021-11-23

- Call annotations are uploaded by a cron to the ERP as CRM and ATC Cases 
- Call logging and annotation simplified in a single log (Breaks backward compatibility)
- persons.yaml is created the first time Tomatic is run

- Call Info: New alert for self-comsumption contracts
- Fix: person color sliders set to initial values
- Persons have a new field: ERP User
- Accessibility: White for text in person boxes with dark colors

## 4.2.4 2021-11-22

- Documentation: Added user guide with screenshots and videos
- Documentation: README splitted and reorganized
- CI/CD Migrated from Travis to Github Actions
- Scripts moved to a folder and used thought PATH

## 4.2.3 2021-11-12

- Callinfo: Fix: crash when no readings or no invoicings or no meters

## 4.2.2 2021-11-12

- Callinfo: 1:20 speedup on getting contract details of a partner with 16 contracts

## 4.2.1 2021-11-11

- Callinfo: Fix: atr cases were not visible in kumato mode
- Callinfo: Contract details in tabs (atr, invoices, readings)
- Callinfo: Displaying person's roles on the contract roles got some care
- Callinfo: Fix: invoice background used to separate invoices

## 4.2.0 2021-11-11

- Tomatic frontend reload when a new version in the server is detected
- Callinfo: Contract details include full informed ATR cases
- Callinfo: Support administrator role
- Callinfo: Show contract owner NIF
- Callinfo: Show state of contracts (previously just showed city, not informative for small towns)
- Callinfo: Display multiple powers for each period
- Callinfo: Button to update crm categories from the ERP
- Callinfo: Do not crash when no contracts available
- Callinfo: Unified questionary checkboxes in single question
- Callinfo: Rethought texts in case resolution dialog

## 4.1.1 2021-11-09

- Fix: port param to upload static timetables was ignored

## 4.1.0 2021-09-27

- Take festivities (public holidays) from odoo
- All scripts are installed when installing tomatic
- New script `areavoip_callapi.py` to call Area Voip API entry points from CLI
- New script `tomatic_retriever.py` to diagnose file retrieval problems
- Removed scripts `tomatic_sandbox.py`

## 4.0.3 2021-09-06

- Fix: supporting removed hangout accounts which had emails as None, not []
- New default channel for team communication

## 4.0.2 2021-07-13

- Fix: retireold api url not available because of url priority in fastapi
- Annotations without Contract or partner may have claims
- Annotation icon moved to the call registry
- Settings icon moved into menu (update claim categories)
- CallInfo: No need to report estimatable contracts anymore

## 4.0.1 2021-06-21

- Removing Spain prefix from callerids as the partner sends them
- Websocket connection moved from / to /backchannel
- Timetable changelog fully displayed
- Fix: callinfo: empty contracts returned as 'polisses'
- Fix: search field select changes when programmatically changes
- Fix: better behaviour and information on missing stuff
  (contracts, readings, invoices...)

## 4.0.0 2021-06-21

- Migrated to FastAPI. Fixes using different port for websocket.
- Loading shallow contract data first to speed up response
- Search by contract number
- Rich annotation context (partner name, contract address...)
- Display detail of contract information aside so it can fit
  in one screen and have more information at glance
- Annotation dialog: available always regarding the search and selected call
- Annotation dialog: wider layout
- Annotation dialog: show context, which call, which contract/partner
- Fix: Zero energy invoices now are shown as 0 not blank
- Fix: Better detection changing users on other tabs
- Implementation changes
  - Callinfo model and view split so that subviews can acces common state directly
- Menú options to planter and scripts
- Kumato mode (dark style)

## 3.11.0 2021-06-15

- Call info
  - Interface redesigned to be responsive and more usable
  - Manual annotations (without an incomming call)
  - Colored scrollable call log
  - Backend info stored in a single directory
  - More reliable backend info storage
- Server has --queue option to enable a second 
  Tomatic instance with a testing queue to make
  experiments
- Searches can be registered as atc/info cases
  without having to receive an incomming call

## 3.10.2 2021-05-28

- Avoid crashing when having no claims type file
- Automatic queue status refresh with animations

## 3.10.1 2021-05-24

- Default vacations source odoo instead of drive
- Fix: missing import tomatic.persons on retriever for odoo
- Callinfo files reorganized

## 3.10.0 2021-05-05

- Improved deployment
- Dropped Python 2 support
- Monitor agents not connected, notified by hangouts
- Vacations taken from odoo
- Split scheduler into retriever and backtracker
- Queues: Display queue agents status with styles
- CallInfo: Nicer user interface
- Callinfo: Refactoring ui in separated components
- Callinfo: Added more contract information (meter readings, invoices...)
- Callinfo: Calls register now saved in local (not in drive)
- Callinfo: Added claims script to save cases to ERP

## 3.9.3 2021-03-27

- Areavoip stats history available in the scriptlauncher
- Script to reset accomulated credit/debit
- `tomatic_shiftload`
	- option `--forgive` to not take any debit or credit from the past
	- option `--summary file.tsv` dumps the stages of the computation
	- all those options made available in script launcher

## 3.9.2  2021-02-24

- FIX: arevoip api requires new parameter to add agents to queue

## 3.9.1  2021-02-12

- `areavoip_dailyreport.py` dumps daily stats in a csv
- `areavoip_dailyreport.py` temporary wrapper to run it on current server
- FIX: missing dependency on emili

## 3.9.0  2021-02-12

- areavoip: Take stats from api and send them daily by mail

## 3.8.0  2021-02-12

- Added 2021 holidays
- Common error handling to all entry points
- areavoip: api calls have a time out, to avoid thread locks
- Fix: areavoip: send 'ids' not 'numbers' in `add` and `clear`
- Fix: `tomatic_rtqueue.py show` repeates table headers and no content
- `tomatic_rtqueue.py` takes `tomatic.areavoip.queue` as default
- areavoip supports extensions interface, adapting
  semantics to assign and remove names instead of adding
  and removing the extensions, a forbiden operation in the platform.
- Api CLI options `--date` and `--time` make fake pbx (`--fake`)
  to preload the queue at that moment acording to the timetables.
- Persons rule:
	- Fix: Persons information no more queried to the timetable
		but the persons module based on `persons.yaml`
	- Queue `pause`, `add` and derivatives are safely ignored
		when the person has no extension in persons.yaml
	- `persons.update()` to centralize info updating
- Refactorings to unify pbx backends interfaces
	- Operations in PBX backends dealing with timetibles
	  have been extracted out
	- `ScheduleStorage.queueScheduleFor` can provide
	  a queue for a given time
	- Api uses a wrapper which methods have an implicit default queue
- Cleaned some of the test warnings

## 3.7.0  2020-11-30

- PBX backend to use the Areavoip (Nubelphon) API
- PBX backends now use agent ids instead extensions
- scriptlauncher: Fix: failed to load because of colons in titles
- Added a nice favicon
- Few remaining Py3 fixes

## 3.6.5  2020-09-16

- Fix: shiftload stalled when compensation don't get a better credit
- Fix: scriptlauncher entry for `tomatic_says` failed
- Cron warn each operator by hangouts individually on new turn
- Experimental API /api/persons/extension/<extension> to get the email for a given extension
- Documentation:
	- How to upgrade

## 3.6.4  2020-06-04

- Documentation:
    - How to setup drive data sources
    - How to setup Hangouts notifications
- Dependency fixes for old Python2
- `tomatic_says.py`:
    - Migrated to `async/await` syntax (unsupported by python 3.4 and earlier)
    - README indicates how to setup: authentication, token files...
    - new option `-t,--tokenfile` to change the default token file (implies changing sender)
    - new option `-c,--channel` to change the default target of the message (config.yaml/hangoutsChannel)
    - Addressing a conversation by full name or hangouts id (base64 code)
    - Addressing a person by tomatic id, email, full hangouts name, or hangouts `gaia_id` (21 digits)
    - When target is not found a list of available targets is displayed

## 3.6.3  2020-06-03

- Penalties info is included in html timetable uploaded to the tomatic-static website
- Penalties info is included in html timetable shown in the planner execution result
- Busy reasons are displayed in planner when hovering over the blocking time slot

## 3.6.2  2020-06-01

- api: `--ring` option to enable incoming call notifications
- `tomatic_busy.py`
	- explains the reasons why people is busy each time
	- takes persons from ponderatedIdeal
	- scriptlauncher item to call it

## 3.6.1  2020-05-18

- Auto-backup timetables on edit and upload
- Fix: planner upload does it locally instead of calling manual upload api
- Cron setup documented
- `tomatic_says.py` Target channel configured in config.yaml
- Callinfo: Fix: downloading complaint reason freezed flask
  threads while downloading info from drive. Tomatic load should be faster.

## 3.6.0  2020-05-11

- Web frontend to launch and monitor sandboxed schedulers /api/planner

## 3.5.1  2020-04-29

- FIX: Health leaves had no effect in capacity
- Entry point and script launcher to retire old timetables

## 3.5.0  2020-03-20

- New functionality to keep track of shift credit across weeks
- Day-off retrieval from notoi API
	- Relates by emails
	- Removed config params that shoud be constants
	- Extracted Notoi proxy class
- New script: `tomatic_uploadtimetable.py`
- API: download shiftload and overload from last
	`tomatic_shiftload.py` execution for the week
	- /api/shifts/download/shiftload/<week>
	- /api/shifts/download/overload/<week>

## 3.4.0  2020-03-09

- New script: `tomatic_shiftload.py` to automate weekly load generation
- New script: `tomatic_mergedicts.py` to perform person by person manipulations
	in person->value yaml dicts (add, substract, extract 
- script `scheduler.py` renamed as `tomatic_schedule.py`
- Scheduler: `--lines` option to indicate the number of lines
- Scheduler: `--personsfile` option to indicate the persons file
- Scheduler: Holidays are automatically removed from search days
- Scheduler: Fix: people without table (ningu) is in table -1 (None)

## 3.3.1  2020-02-24

- Fixes on persons.yaml split
- Travis compilation

## 3.3.0  2020-02-24

- Py3 compatibility
- Scheduler: algorithm modifications to indiscriminate lines
- Persons information is splitted out of the config.yaml file into persons.yaml
- Scheduler: busy files and person info are downloaded from tomatic api
- Scheduler: B2B tested, required stop conditions and deterministic execution

## 3.1.0  2019-10-18

- Callinfo: ability to fill claims

## 3.0.0  2019-07-24

- Call info
- User identification
- Must identify before edit schedule

## 2.1.0  2018-02-07

- First tagged release 


