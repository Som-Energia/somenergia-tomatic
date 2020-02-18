# Glossari bilingüe

Donat que sovint el vocabulari és confús i polisèmic,
per a una comunicació eficient
entre IT i les persones que definiran els requeriments,
i dintre d'IT,
a continuació definim en concret un glossari de conceptes.

També posem al costat el mot en anglès per facilitar la seva
incorporació en el codi font.

- **persona:** (_person_) Cadascuna de les persones que poden rebre trucades
- **dia:** (_day_) Cadascun dels dies de la setmana (dl, dm, dx, dj, dv)
- **hora:** (_hour_) Cadascuna de les hores a la que comecen els torns (9:00, 10:15, 11:30, 12:45)
- **linia:** (_line_) Les diferents linies que poden estar rebent trucades en un torn
- **torn:** (_turn_) Conjunció de hores i dies. Exemple el torn de dimarts a les 9h

- **cassella:**
  \footnote{David: A la cassella se li diu sovint torn, hi ha cap mot que expressi el que queda definit com a torn?}
  (_cell_) Conjunció de dia, hora, i linia. Exemple la casella de dimarts a les 9h per la linia 1 (primaria).
- **linies discriminades:** (_discriminated lines_)
  Succeeix quan hi ha diferencia entre les linies.
  Per exemple si acaba tenint més trucades una primera que una sisena linia.
- **indisponibilitat:** (_busy_) el fet de que una persona no estigui disponible per un torn concret
- **indisponibilitat fixa:** (_weekly busy_) La que succedeix cada setmana
- **indisponibilitat puntual:** (_oneshot busy_) La que succedeix puntualment un dia
- **indisponibilitat opcional:** (_optional busy_) La que es podria negociar en cas de que no hi hagi graelles viables.
- **indisponibilitat forçosa:** (_unavoidable busy_) La que no es pot negociar
- **càrrega:** (_load_) Nombre de torns que fa algú en una setmana. Pot ser discriminada per linies o no
- **càrrega ideal:** (_ideal load_) Càrrega que asumeix setmanalment cada persona pel seu perfil i antiguitat
- **absència alliberadora** (_free day off_) Indisponibilitats que redueixen la càrrega setmanal d'una persona.
    Ara considerem alliberadores: Festius, vacances, baixes i viatges laborals
- **càrrega ponderada:** (_ponderated load_) Càrrega proporcional que una persona ha d'assumir una setmana en concret, considerant les absències alliberadores.
    Exemple: Si una persona té ideal 4 torns, i aquella setmana té 2 dies de vacances, només haurà de fer $4 (5-2)/5= 2.4$.
- **càrrega arrodonida:** (_rounded load_) Càrrega ponderada arrodonida, donat que la cárrega ponderada surt d'un factor amb decimals
- **capacitat d'una persona:** (_person capacity_)
    Els torns que pot fer una persona una setmana en concret tenint en compte les seves indisponibilitat i les restriccions que s'imposin en com distribuir les hores.
    - Mai es faran més de 2 torns diaris
    - Si es fan 2 torns, han de ser les 2 hores primeres o les 2 darreres
        - Per concentrar les hores de telèfon i no partir massa el matí
        - Per deixar temps a mig matí per esmorzar

- **càrrega limitada:** (_bounded load_) Càrrega ajustada per no superar la capacitat de la setmana de la persona.
- **bossa de torns:**
    (_turn bag_) Annotació acomulada per a cada persona
    de quants torns ha acabat fent en el passat més o menys respecte la càrrega arrodonida que li tocava cada setmana.
    \footnote{David: Dubto si fer-ho respecte a l'arrodonida o la ponderada sense arrodonir}
- **creditora:** persona a la que se li deuen hores que ha fet de més
- **deutora:** persona que deu hores que ha fet de menys
- **càrrega final:** (_final load_)
    Càrrega final que ha de fer cada persona, compensant deutes i/o generant-ne de nous
    per arribar al nombre de casselles.
    - Restriccións
        - Les càrregues finals de tothom han de sumar el nombre de casselles
        - Ningú hauria de tenir més torns que la ponderada + 1
        - Ningú hauria de tenir més torns que la seva capacitat
    - Criteris
        - Fins arribar al nombre de casselles, fer servir credit i deute de la bossa d'hores
            - S'escull entre les que més crèdit o deute tinguin
        - Si s'arriba, compensar credit amb deute fins que un sigui zero o no es pugui fer sense violar restriccions
        - Si no s'arriba, generar deute i crèdit nou aleatoriament entre els que menys en tinguin



