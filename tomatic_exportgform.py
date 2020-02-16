#!/usr/bin/env python

from __future__ import print_function
from sheetfetcher import SheetFetcher
from tomatic import busy
from yamlns import namespace as ns
import codecs
config = ns.load('config.yaml')

# Dirty Hack: Behave like python3 open regarding unicode
def open(*args, **kwd):
	return codecs.open(encoding='utf8', *args, **kwd)


fetcher = SheetFetcher(
	documentName='Quadre de Vacances',
	credentialFilename='drive-certificate.json',
	)
indis = fetcher.get_fullsheet(config.fullIndisponibilitats)
singulars = busy.gform2Singular(indis)
with open('oneshot.conf', 'w') as f:
	for singular in singulars:
		if not singular.reason:
			singular.reason="Motiu sense especificar"
		line = busy.formatItem(singular)
		print (line)
		f.write(line)

print(busy.busy('erola').dump())

