# Restriccions i penalitzacións de l'arbre de cerca

**Restricció:** Fa que una graella no sigui viable.

Perquè és util definir-ne?

La cerca de la graelles es fa provant, per cada cassella de la graella, cadascuna de les persones.
Per explorar totes les possibilitats cal recòrrer un arbre de decissió inmens.
Té tants nivells com caselles de la graella (6 linies x 5 dies x 4 hores = 120 caselles),
i a cada nivell les branques es multipliquen pel nombre de persones.

Detectar una restricció a una solució parcial (quan només hem omplert unes poques caselles),
ens permet podar l'arbre i reduir el recorregut.

**Penalització:** Fa que una graella es consideri pitjor que una altra.

Perquè és util definir-ne?

Principalment, ens permeten decidir quina és la millor d'entre dues solucions viables.

Assignem a cada situació que volem evitar una penalització en punts negatius.
Serà millor la solució que menys penalització acomuli.

Un cop obtenim la primera solució viable,
podem podar les solucions parcials que superin la penalització de la millor solució trobada.


Les restriccions i penalitzacions implementades són les següents:

## Restriccions

- **Busy**\
    La persona no està disponible pel torn que s'està repartint.
    Pot ser per indisponibilitat o perqué ja l'hem posat a una altra linia
    el mateix torn.

- **FullLoad**\
    A la persona no li queden torns a colocar (amb discriminació,
    no té torns de la linia a la que correspon la casella)

- **Redundant**\
    Quan no hi ha discriminació de lines, talla les solucions que només
    reordenen les persones d'un torn. S'activa amb `pruneRedundant`

- **FullDay**\
    La persona ha superat el seu màxim nombre d'hores diaries.
    Es defineix en general a `maximHoresDiariesGeneral`
    o especificament per la persona a `maximHoresDiaries`.
    Actualment el general es 2 i només fem servir el especific
    per `ningu` o quan es una graella molt complicada i volem fer
    una excepció.

- **MassesPrincipals** (obsolete)\ 
    Quan hi ha discriminació de linies,
    podem limitar els torns primaris (L1) que fa una persona per dia.\
    Es defineix a `maximsT1PerDia` i normalment és 1.\

- **Crosstalk**\
    Per evitar crosstalking, limitem a `maximPerTaula` (per defecte, 2)
    la gent que pot estar rebent trucades assegudes a la mateixa taula.
    Per això definim les taules a la interficie web del Tomatic.
    Hi ha una penalització (Crosstalk) per abans d'arribar al màxim.

- **NotEnoughIdleInGroup**\
    S'ha definit que, en un grup de gent, ha d'haver un cert nombre
    mínim de persones senser fer telèfon i s'ha trencat la restricció.
    Per exemple, si ha d'haver algú d'IT per resoldre incidències.

- **TooManyLinesForGroup**\
    S'ha definit que, en un grup de gent, no pot haver més d'un cert
    nombre de persones fent telèfon.
    Per exemple, si volem limitar les persones parlant en un espai.
    De fet la majoria de grups definits son per aquest motiu.

- **Brunch**\
    Estem posant un tercer torn a una persona que està fent el segon torn
    del mateix dia, això vol dir que no tindrà el temps que otorga la POL per esmorzar.
    Es pot deshabilitar globalment amb `deixaEsmorzar` o per una persona
    afegint-la a la llista `noVolenEsmorzar`.

- **Discontinuous**\
    La persona ja té hores posades el mateix dia però no són consecutives.
    Es converteix en una penalització a les persones amb un maxim de torns major que 2

- **TooMuchCost**\
    La solució parcial ja supera el cost de la millor solució total trobada.

- **CostEqual**\
    La solució parcial iguala el cost de la millor solució total trobada
    i només hem posat un 70% de les casselles.\
    Nota: No se si aquesta restricció fa gaire cosa, o, si en fa, de bona.

- **NoEarlyCost**\
    La solucio parcial és poc prometedora.
    Només afecta quan ja tenim una solucio complerta,
    si la parcial té un cost per día superior a la complerta.
    Es fa amb la benentesa de que molts dels costos s'afegeixen a les darreres casselles.

- **TooManyConcurrentHoles**\
    La solució té massa forats simultanis (línies amb `ningu` al mateix dia i hora)
    superant el nombre configurat `maxNingusPerTurn`.

A mirar en començar a omplir un dia:

- **L1RestantsIncolocables**\ (Obsolete)
    A una persona no li queden forats per ficar tota la seva càrrega de primeres linies.
    Normalment vol dir que hauriem d'haver colocat el seus torns de primera linia en dies anteriors.
    Està a part perque, si discriminem linies, les primeres linies estan restringides
    a una per dia (`maximsT1PerDia`) i ens permet descartar abans.

- **UnableToAllocateLoad**\
    A una persona no li queden forats per ficar tota la seva càrrega.
    Normalment vol dir que hauriem d'haver colocat el seus torns abans.

## Penalitzacións

- **Discontinuous** `costHoresDiscontinues`\
    La persona ja té hores posades el mateix dia però no són consecutives.\
    Es converteix en una restricció a les persones amb un maxim de torns menor que 3\
    Objectiu: Procurar no interrompre la feina normal amb hores de telèfon

- **Undesired** `costHoraNoDesitjada`\
    La persona ha de fer un torn que té marcat com a indisponibilitat opcional.
    Objectiu: Respectar el màxim de indisponibilitats opcionals

- **ConcentratedLoad** (`costHoresConcentrades` * número d'hores anteriors)\
    La persona ja tenia col·locades més hores el mateix dia.\
    Objectiu: Afavoreix que els torns es reparteixin al llarg de la setmana.

- **Crosstalk** (`costTaulaSorollosa` * altres persones parlant a la taula)\
    La persona farà telèfon simultàneament amb altres persones que es
    seuen juntes a la mateixa taula\
    Objetiu: Reduir l'efecte de converses creuades quan tens una altra 
    persona fent telèfon al costat i repartir espaialment el soroll generat

- **ConcurrentHoles** (`costTornBuit` * nombre de casselles amb `ningu` a la mateixa hora i dia)  \
    Es col·loca un `ningu` a la graella.
    Objectiu: Que els forats/`ningu` es reparteixin en diferents dies

