#!/bin/bash

PYTHONIOENCODING=utf8 ./tomatic_calls.py summary |
while read a
do
	./tomatic_says.py "$a"
done
./tomatic_says.py "Recordeu anotar les trucades: https://intranet.helpscoutdocs.com/article/749-formulari-telefon-inquietuds-clients"


