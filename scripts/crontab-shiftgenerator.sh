#!/bin/bash
# To setup those task you should:
#    sudo chown root:root crontab
#    sudo chmod 755 crontab


executor_id=$(./scripts/tomatic_shiftgenerator.py)
echo $executer_id 
sleep 1  # TODO: cuanto?


echo ${executer_id}

./scripts/tomatic_shiftmanager.py --${executor_id}

