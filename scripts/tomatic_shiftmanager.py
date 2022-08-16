#!/usr/bin/env python


import sys
import requests
import yaml
from emili import sendMail 
from io import open
from yamlns import namespace as ns


execution_id = sys.argv[1]

config = ns.load('config.yaml')


statusuri = config.baseUrl + f"/api/planner/api/status/{execution_id}"
stopuri = config.baseUrl + f"/api/planner/api/stop/{execution_id}"
uploaduri = config.baseUrl + f"/api/planner/api/upload/{execution_id}"
killuri = config.baseUrl + f"/api/planner/api/kill/{execution_id}"

# TODO: maybe already stopped
stop = ns.loads(requests.get(stopuri).content).get('ok')
if not stop:
    kill = requests.get(killuri)

status = ns.loads(requests.get(statusuri).content)


if status.unfilledCell == "Completed":
    response = requests.get(uploaduri)
else:
    pass
    #TO DO implement send email
    # send email

