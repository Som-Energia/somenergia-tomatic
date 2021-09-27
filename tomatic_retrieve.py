#!/usr/bin/env python3

from yamlns import namespace as ns
from yamlns.dateutils import Date
from tomatic.retriever import downloadVacations, downloadFestivities
from tomatic.persons import persons

config=ns.load("config.yaml")
config.monday = Date("2021-03-29")
config.update(persons())
downloadFestivities(config)
downloadVacations(config, 'odoo')
#downloadVacations(config, 'drive')
#downloadVacations(config, 'notoi')


