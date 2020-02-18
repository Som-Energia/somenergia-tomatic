# Logica de compensació d'hores

1. **Càrrega ideal:** Es parteix de les càrregues ideals del drive
1. **Càrrega ponderada:** Aquesta carrega es ponderarà pels dies hàbils de cada persona on es tenen en compte (ideal * dies habils / 5)
    - Els dies hàbils són els que no són
        - Festius
        - Vacances
        - Baixes
        - Viatges laborals
1. **Càrrega arrodonida:** La càrrega ponderada s'arrodonirà a torns sencers.

1. **Càrrega limitada:** Es reduirà la càrrega arrodonida amb la capacitat real de cada persona degut a indisponibilitats no opcionals
    - Per saber quina es aquesta capacitat màxima cal veure cada dia com casen les indisponibilitats amb aquestes restriccions:
        1. Cada persona no pot fer més de dos torns un dia
        1. Per fer dos torns han de ser seguits bé a l'inici o bé al final del dia

1. **Càrrega final:** Compensació:
    - És possible que fent això estiguem per damunt o per sota dels torns necessaris
    - També és possible que hi hagi deutes de torns antics que calgui compensar
    - Cas: Torns arrodonits 122, a fer 120
        - Primer compensem els 2 que sobren amb bossa que debem, un a cadascú, començant pel que en té més, reprtint si calgués
        - Si arribem a 120, seguim compensant la bossa que debem amb la bossa que ens deuen, seleccionant els que deuen començant pel que en deu més
        - Si no arribem als 120, alliberem a gent que no deu, i li posem a la bossa d'hores com deute
    - Cas: Torns arrodonits 118, a fer 120
        - Primer compensem els dos que falta amb bossa d'hores que en deuen
        - Si arribem a 120, seguim compensant bossa d'hores que ens deuen amb bossa d'hores que debem
        - Si no no arribem a 120, carreguem a gent que no li debem, i li posem a la bossa d'hores com que li debem
    - Cas: Torns arrodonits 120, a fer 120
        - Si arribem a 120, compensem bossa d'hores que ens deuen amb bossa d'hores que debem

    - Restricccions:
        - Limit: ideal + 1 per persona
        - Capacitat per indisponibilitats matatives
        - Per sota em podria quedar sense torns

1. La diferencia entre càrrega final  

    - El que no es pugui fer de la càrrega ponderada perque no hi ha capacitat, es posa com a deute a la bossa d'hores
    - S'agafarà aquesta càrrega com a referència per dirimir els torns que es deuen per la graella.















