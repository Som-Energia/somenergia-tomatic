#!/usr/bin/env python

__doc__ = """\
This script uploads a timetable (as yaml file)
to the Tomatic server (at the uri indicated
in config.yaml as baseUrl)
"""

import sys
import requests
from io import open
from pathlib2 import Path
from yamlns import namespace as ns

timetablefile = Path(sys.argv[1])

config = ns.load('config.yaml')
timetable = ns.load(str(timetablefile))
uploaduri = config.baseUrl + "/api/graella"

r = requests.post(
	uploaduri,
	files=dict(yaml=timetablefile.open(encoding='utf8'))
	)
print(r.content)
print(dir(r))

