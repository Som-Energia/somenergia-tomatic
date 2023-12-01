#!/bin/bash
# To setup those task you should:
#    sudo chown root:root crontab
#    sudo chmod 755 crontab

MESSAGE_FILE=data/turn-change-message.txt

turn=$(tomatic_rtqueue.py preview --time $(date -d '10 minutes' +'%H:%M') )

tomatic_says.py "Canvi de torn en 5m: $turn"
if [ -e "$MESSAGE_FILE" ]; then
    cat "$MESSAGE_FILE" | while read LINE; do
        tomatic_says.py "$LINE"
    done
else
    tomatic_says.py "Dubtes a la intranet: https://intranet.helpscoutdocs.com/"
    tomatic_says.py "Info de trucada entrant a http://tomatic.somenergia.coop/#/Trucada"
fi

#To Do: send personal chats
#for person in $turn
#do
#	tomatic_says.py -c ${person/,/} "Hola super, tens torn de telefon en 5 minuts!"
#done

