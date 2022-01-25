# TODO's

## Backlog

- [ ] Remove config.yaml from git (backup the file to use it in production)
- [ ] Configurable timetable directory ('graelles')
- [ ] Configurable execution directory ('executions')
- [ ] Move shiftload generated files to a configurable dir (maybe same as timetables dir?)
- [ ] `Claim.get_claims` -> Claim.get/update/retrieveClaimTypes
- [ ] As an agent i want to be able to see cancelled contracts in callinfo (pe. for claims of unauthorized switching)
- [ ] Call Info: Report diferently, search cleared from no search found
- [ ] Call Info: Intercept backend connection errors and behave
- [ ] Call info: List previous calls from same person/contract
- [ ] Unify call log also into the case log
- [ ] Google login
- [ ] API tests in fastapi
- [ ] Accept fragile erp tests
- [ ] Strip spaces in the search
- [ ] Edit previous annotations
- [ ] On ringing sandwich pbx ext, and use tomatic users inside (do not log by ext but by user)
- [ ] Translate call log field names from catalan
- [ ] api/info/ringring -> api/call/ringring (ext)
- [ ] /api/personlog/<ext> en els casos de fallada returnar una llista buida sense errors (no son de fallada, encara no hi ha logs i prou)
- [ ] api/personlog/{ext} -> api/call/log/{user}
- [ ] api/updateClaims -> called by cron or init
- [ ] api/updateClaimTypes -> called by cron or init
- [ ] api/updateCrmCategories -> called by cron or init
- [ ] api/getClaimTypes -> api/call/claim/types?
- [ ] api/getInfos -> api/call/info/types?
- [ ] consider joining getClaimTypes and getInfos
- [ ] GSpread docs say that moving the credential to `~/.config/gspread/service_account.json` avoids having to pass it around as parameter
- [ ] `tomatic_calls` should use persons module instead referring persons.yaml directly

- Planner:
	- [ ] Refactor as Single Page App
	- [ ] Style it
	- [ ] Show cutting reasons of best solutions
	- [ ] Ask before deleting, killing, uploading...
- Scheduler:
	- [ ] Join load computation into the scheduler script
- Person editor:
	- [ ] Disable ok until all fields are valid
	- [ ] Check extension not taken already
	- [ ] Check erp user exists
	- [ ] Focus on first dialog field on open
	- [ ] Take person info from holidays manager
	- [ ] List/admin mode
- Callinfo
	- [ ] Simplify yaml structure
	- [ ] Refactor tests
	- Alerts:
		- [ ] Unpaid invoices

## Trello https://trello.com/c/ljKRzvz5/4221-0-3-p7-centraleta-kalinfo-desar-els-casos-de-consultes-del-kalinfo-al-erp

- [ ] Dubte AiS: cal pujar les anotacios que heu fet de proves
- [ ] Dubte AiS: renombrar user -> seccion/team (preguntar a AiS per terminologia de domini)
- [ ] Dubte AiS: tenim les llistes a produccio que fem amb elles (mostrarles perque hi ha brossa i textos que poden canviar)

- [ ] entry point to obtain categories
- [ ] encapsulate access to the categories info in frontend
- [x] callinfo log: unite resolution fields
- [x] callinfo log: join infos and claims
- [ ] callinfo log: join infos/claims with log? (consider performance and usage)
- [x] Importar categories que falten de atc com a categorias de crmcases
- [x] anotate_case: sensitive to the case fields creates atc or not
- [ ] !!! create crm: solved = True (lo comentamos cuando lo movimos a una funcion a parte)
- [ ] create crm: extract seccio del reason and remove the field
- [ ] create crm: cas contracte no existeix
- [ ] callreg: Rename Claims to reflect its repurposing
- [x] callreg: create crm: Inserir usuari correcte al CRM (es fa servir l'usuari loggejat a l'erp: Scriptlauncher i no veiem com canviar-ho)
- [ ] callreg: On failing annotation, ui notifies the user


## Dones


- [x] Use contrast text color for person boxes
- [x] Editable erpuser in PersonEditor
- [x] move scripts to a folder
- [x] Fix: Person color picker sliders are not valued with the initial color
- [x] persons interface: api uses persons
- [x] persons interface: persons() set attributes with ns() if not found
- [x] persons interface: persons.update(person, **kwds)
- [x] persons interface: tomatic_says use persons
- [x] persons interface: scheduler use persons
- [x] persons interface: shiftload uses persons
- [x] pbx interface: use pbx backends instead of current pbx interface
- [x] pbx interface: remove use setScheduledQueue (mostly in tests)
- [x] pbx interface: unify backend interfaces
- [x] pbx interface: dbasterisk works with names not extensions
- [x] Hangouts: Configurable token file path
- [x] Hangouts: Choose output channel by CLI
- [x] Hangouts: Choose token file by CLI
- [x] Hangouts: List channels when no channel has been configured yet
- [x] Refactoritzar codi comu dels getInfoPersonByXXXX
- [x] Optimizar búsquedas callinfo
- [x] Commit `info_cases/info_cases.yaml`
- [x] Commit `claims_dict.yaml`
- [x] /api/claimReasons Deprecated (no ui code aparently)
- [x] /api/infoReasons Deprecated (no ui code aparently)
- [x] /api/callReasons Deprecated (no ui code aparently)
- [x] Translate case field names from catalan
- [x] Call Info: download invoices and metering in a separate query to provide response earlier
- [x] Call Info: Relayout persons and contracts in one side, alarms invoices and meters on the other
- [x] Anotar trucada d'una persona encara no vinculada a som
- [x] Fix: CalRegistry: Selecting twice no longer deselects
- [x] Fix: Cambio de partner -> pestaña 0 de contratos
- [x] Spinner when loading additional
- [x] Search: Update the field whenever automatic search is done
- [x] Annotate: Dissable button if logged out
- [x] Search by contract -> persones vinculades -> contractes vinculats
- [x] Annotate: Context with person name and addresses
- [x] erp connection pool
- [x] Detecting user changed by other tab or cookie timeout
- [x] Call Registry: Codi titular -> Persona atesa
- [x] Change websocket lib to enable sharing http port and debug mode
    - [x] Fast api spike
        - [x] Migrate main api
        - [x] Migrate sockets
        - [x] Migrate planner api
- [x] Fix: annotations save date with miliseconds and duplicates existing entries
- [x] Menu for planner and scripts
- [x] As an agent i want to annotate about a partner having no contracts
- [x] "No estimable" flag is obsolete. No contract is estimable now.
- [x] Contract info: Contract aministrator role (besides TPNS)
- [x] Contract info: Add owner NIF
- [x] Contract info: Add provincia field
- [x] Contract info: Add Contract modification list
- [x] Call Registry: layout shorter and wider on small screens

### 2021-11-12

- [x] Create Claim case
- [x] One endpoint for call registry in API
	- [x] joining updatelog, infoCase and atrCase
	- [x] api/updatelog/{user} -> api/call/annotation (joined)
	- [x] api/infoCase -> api/call/annotation (joined)
	- [x] api/atrCase -> api/call/annotation (joined)
- [x] One method for call registry in CallRegistry
- [x] Bug: Antotacions UI: Radio button no resolt + tenia rao > no tenia rao
- [x] create crm: cas amb tot
- [x] create crm: cas sense contracte
- [x] create crm: cas sense partner
- [x] create crm: te sentit loggejar el cups si tenim el contract id? -> No, fet
- [x] create atc uses create crm
- [x] create atc: cover test cases
- [x] empty kalinfo.crmcase and remove
- [x] Claims.get_claims -> claimCategories()
- [x] callinfo log: do not dump cups



