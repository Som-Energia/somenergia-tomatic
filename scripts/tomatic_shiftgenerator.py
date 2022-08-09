#!/usr/bin/env python
# -*- coding: utf-8 -*-


__doc__ = """\
This script generates a timetable
"""

import sys
import requests
import yaml
from yamlns import namespace as ns

from tomatic.plannerexecution import nextMonday


config = ns.load('config.yaml')
uri = config.baseUrl + "/api/planner/api/run"
nextmonday = nextMonday()

response = requests.post(
	uri,
    params=dict(
        nlines=config.nTelefons,
        monday=nextmonday,
        description=''
    )
)

sys.exit(yaml.load(response.content, Loader=yaml.FullLoader)['execution_id'])
print(response.content)
