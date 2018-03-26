#!/bin/bash

./tomatic_says.py "Canvi de torn en 5m: $(tomatic_rtqueue.py preview --time $(date -d '10 minutes' +'%H:%M') )"
./tomatic_says.py "Recordeu anotar les trucades: https://intranet.helpscoutdocs.com/article/749-formulari-telefon-inquietuds-clients"


