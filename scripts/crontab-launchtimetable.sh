#!/bin/bash

supportmail=$(python -c "from tomatic.config import secrets; print(secrets('tomatic.supportmail'))")
appmail=$(python -c "from tomatic.config import secrets; print(secrets('smtp.user'))")
weeksInAdvance=$(python -c "from tomatic.config import secrets; print(secrets('tomatic.foreplanweeks', 1))")
week=$(LANG=C date +%F -d "next Monday + $weeksInAdvance weeks")
reportrun -C dbconfig.py -f $appmail -t "$supportmail" -s "Tomatic Timetable Laucher Failed" -- tomatic_timetable.py launch $week

