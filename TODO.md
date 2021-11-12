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
- [x] Create Claim case
- [ ] Create Phone Call Case
- [ ] One endpoint for call registry in API
- [ ] One method for call registry in CallRegistry
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
- [ ] api/updatelog/{user} -> api/call/log/update/{user}
- [ ] api/infoCase -> api/call/annotation
- [ ] api/atrCase -> api/call/annotation (joined)
- [ ] consider joining updatelog, infoCase and atrCase
- [ ] api/updateClaims -> cron or init
- [ ] api/updateClaimTypes -> cron or init
- [ ] api/updateCrmCategories -> cron or init
- [ ] api/getClaimTypes -> api/call/claim/types?
- [ ] api/getInfos -> api/call/info/types?
- [ ] conisider joining getClaimTypes and getInfos


- [ ] moure scripts a una carpeta

- [ ] Antotacions UI: Radio button no resolt + tenia rao > no tenia rao
- [ ] Anotacions: Unificar Api anotacio en un punt d'entrada
- [ ] Anotacions: Unificar els fitxers d'anotacio i log de trucada
- [ ] Importar categories que falten de atc com a categorias de crmcases
- [ ] create crm: Inserir usuari correcte al CRM
- [ ] anotate_case: sensitive to the case fields creates atc or not
- [x] create crm: cas amb tot
- [x] create crm: cas sense contracte
- [x] create crm: cas sense partner
- [x] create atc uses create crm
- [ ] !!! create crm: solved = True (lo comentamos cuando lo movimos a una funcion a parte)
- [x] create atc: cover test cases
- [x] empty kalinfo.crmcase and remove
- [ ] create crm: renombrar user -> seccion/team (preguntar a AiS per terminologia de domini)
- [ ] create crm: extract seccio del reason and remove the field
- [ ] create crm: cas contracte no existeix
- [x] create crm: te sentit loggejar el cups si tenim el contract id?
- [ ] Claims.get_claims -> claimCategories()
- [ ] repurpose claims

- [ ] callinfo log: do not dump cups
- [ ] callinfo log: unite resolution
- [ ] callinfo log: join infos and claims
- [ ] Check: sections id's unlikely to refer the same id (table) in atc and crm
- [ ] On failing annotation, notify the user








