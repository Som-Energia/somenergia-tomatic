# TODO's

## Backlog

- [ ] `Claim.get_claims` -> Claim.get/update/retrieveClaimTypes
- [ ] As an agent i want to be able to see ended contracts in callinfo (pe. for claims of unauthorized switching)
- [ ] Call Info: Report diferently, search cleared from no search found
- [ ] Call Info: Intercept backend connection errors and behave
- [ ] Call info: List previous calls from same person/contract
- [ ] Google login
- [ ] API tests in fastapi
- [ ] Accept fragile erp tests
- [ ] Fix: Person color picker does not pick initial color
- [ ] Strip spaces in the search
- [ ] Edit previous annotations
- [ ] Use contrast text color for person boxes
- [ ] Sandwich pbx ext from ringring, and use users all along
- [ ] Translate log field names from catalan
- [ ] api/info/ringring -> api/call/ringring (ext)
- [ ] api/personlog/{ext} -> api/call/log/{user}
- [ ] api/updateClaims -> cron or init
- [ ] api/updateClaimTypes -> cron or init
- [ ] api/updateCrmCategories -> cron or init
- [ ] api/getClaimTypes -> api/call/claim/types?
- [ ] api/getInfos -> api/call/info/types?
- [ ] consider joining getClaimTypes and getInfos
- [ ] moure scripts a una carpeta

## Trello https://trello.com/c/ljKRzvz5/4221-0-3-p7-centraleta-kalinfo-desar-els-casos-de-consultes-del-kalinfo-al-erp

- [ ] Dubte AiS: cal pujar les anotacios que heu fet de proves
- [ ] Dubte AiS: renombrar user -> seccion/team (preguntar a AiS per terminologia de domini)
- [ ] Dubte AiS: tenim les llistes a produccio que fem amb elles (mostrarles perque hi ha brossa i textos que poden canviar)

- [ ] callinfo log: unite resolution fields
- [ ] callinfo log: join infos and claims
- [ ] callinfo log: join infos/claims with log? (consider performance and usage)
- [ ] Importar categories que falten de atc com a categorias de crmcases
- [ ] anotate_case: sensitive to the case fields creates atc or not
- [ ] !!! create crm: solved = True (lo comentamos cuando lo movimos a una funcion a parte)
- [ ] !! create crm/atc: Check: we are using same ids for atc and crm sections and it is unlikely to be like that since they belong to different tables
- [ ] create crm: extract seccio del reason and remove the field
- [ ] create crm: cas contracte no existeix
- [ ] Rename Claims to reflect its repurposing
- [ ] create crm: Inserir usuari correcte al CRM (es fa servir l'usuari loggejat a l'erp: Scriptlauncher i no veiem com canviar-ho)

- [ ] On failing annotation, ui notifies the user


## Dones


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



