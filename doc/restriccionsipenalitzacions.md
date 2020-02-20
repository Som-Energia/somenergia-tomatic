# Restriccions i penalitzacións de l'arbre de cerca


## Restriccions

- **L1RestantsIncolocables**
    A una persona no li queden forats per ficar tota la seva càrrega de primeres linies.
    Normalment vol dir que hauriem d'haver colocat el seus torns de primera linia en dies anteriors.
    Està a part perque, si discriminem linies, les primeres linies estan restringides
    a una per dia (`maximsT1PerDia`) i ens permet descartar abans.

- **RestantsIncolocables**
    A una persona no li queden forats per ficar tota la seva càrrega.
    Normalment vol dir que hauriem d'haver colocat el seus torns abans.

- **Redundant**
    Quan no hi ha discriminació de lines, talla les solucions que només
    reordenen les persones d'un torn. S'activa amb `pruneRedundant`

- **TotColocat**
    La persona no té torns a colocar (amb discriminació,
    no té de la linia a la que correspon la casella.

- **Indisponible**
    La persona no està disponible pel torn que s'està repartint

- **MassesPrincipals**
    Quan hi ha discriminació de linies, podem limitar a una L1 per dia


- **TaulaSorollosa**
    Per evitar crosstalking, limitem a `maximPerTaula` (per defecte, 2)
    la gent que pot estar rebent trucades assegudes a la mateixa taula.
    Per aixo definim les taules a la interficie web del Tomatic.


- **NotEnoughIdleInGroup**
    S'ha definit que, en un grup de gent, ha d'haver un cert nombre
    mínim de persones senser fer telèfon i s'ha trencat la restricció.
    Per exemple, si ha d'haver algú d'IT per resoldre incidències.

- **TooManyLinesForGroup**
    S'ha definit que, en un grup de gent, no pot haver més d'un cert
    nombre de persones fent telèfon.
    Per exemple, si volem limitar les persones parlant en un espai.
    De fet la majoria de grups definits son per aquest motiu.

- **DiaATope**
    La persona ha superat el màxim nombre d'hores diaries definides
    a `maximHoresDiariesGeneral` o especificament per la persona a
    `maximHoresDiaries`.
    Actualment el general es 2 i només fem servir el especific
    per `ningu` o quan es una graella molt complicada i volem fer
    una excepció.

- **Esmorzar**
    Estem posant un tercer torn a una persona que està fent el segon torn
    del mateix dia, això vol dir que no tindrà el temps que otorga la POL per esmorzar.
    Es pot deshabilitar globalment amb `deixaEsmorzar` o per una persona
    afegint-la a la llista `noVolenEsmorzar`.

- **Discontinu**
    La persona ja té hores posades el mateix dia però no són consecutives.
    Es converteix en una penalització a les persones amb un maxim de torns major que 2

- **TooMuchCost**
    La solució parcial ja supera el cost de la millor solució total trobada.

- **CostEqual**
    La solució parcial iguala el cost de la millor solució total trobada
    i només hem posat un 70% de les casselles.


## Penalitzacións

- **Discontinu** `costHoresDiscontinues`\
    La persona ja té hores posades el mateix dia però no són consecutives.\
    Es converteix en una restricció a les persones amb un maxim de torns menor que 3\
    Objectiu: Procurar no interrompre la feina normal amb hores de telèfon

- **Undesired** `costHoraNoDesitjada`\
    La persona ha de fer un torn que té marcat com a indisponibilitat opcional.
    Objectiu: Respectar el màxim de indisponibilitats opcionals

- **Repartiment** (`costHoresConcentrades` * número d'hores anteriors)\
    La persona ja tenia col·locades més hores el mateix dia.\
    Objectiu: Afavoreix que els torns es reparteixin al llarg de la setmana.

- **Crosstalk** (`costTaulaSorollosa * altres persones parlant a la taula)\
    La persona farà telèfon simultàneament amb altres persones que es
    seuen juntes a la mateixa taula\
    Objetiu: Reduir l'efecte de converses creuades quan tens una altra 
    persona fent telèfon al costat i repartir espaialment el soroll generat















