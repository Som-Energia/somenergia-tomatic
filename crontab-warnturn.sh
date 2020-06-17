#!/bin/bash

turn=$(tomatic_rtqueue.py preview --time $(date -d '10 minutes' +'%H:%M') )
./tomatic_says.py "Canvi de torn en 5m: $turn"
./tomatic_says.py "Recordeu anotar les trucades: https://intranet.helpscoutdocs.com/article/749-formulari-telefon-inquietuds-clients"

for person in $turn
do
	./tomatic_says.py -c ${person/,/} "Hola super, tens torn de telefon en 5 minuts!"
done

