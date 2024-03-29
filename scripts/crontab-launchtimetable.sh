#!/bin/bash

supportmail=$(python -c "import dbconfig; print(dbconfig.tomatic.supportmail)")
appmail=$(python -c "import dbconfig; print(dbconfig.smtp.user)")
weeksInAdvance=$(python -c "import dbconfig; print(dbconfig.tomatic.get('foreplanweeks', 1))")
week=$(date +%F -d "next Monday + $weeksInAdvance weeks")
reportrun -C dbconfig.py -f $appmail -t "$supportmail" -s "Tomatic Timetable Laucher Failed" -- tomatic_timetable.py launch $week

