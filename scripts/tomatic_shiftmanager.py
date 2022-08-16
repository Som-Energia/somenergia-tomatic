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

stop = yaml.load(requests.get(stopuri).content, Loader=yaml.FullLoader)['ok']
if not stop:
    kill = requests.get(killuri)

status = requests.get(statusuri)
unfilledCell = yaml.load(status.content, Loader=yaml.FullLoader)['unfilledCell']
name = yaml.load(status.content, Loader=yaml.FullLoader)['name']


if unfilledCell == "Completed":
    response = requests.get(uploaduri)
else:
    pass
    #TO DO implement send email
    # send email

