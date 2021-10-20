#!/usr/bin/env python3

from yamlns import namespace as ns
from yamlns.dateutils import Date
from tomatic.persons import persons
from consolemsg import step
import datetime
from pathlib import Path


def parseArgs():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--keep',
        action='store_true',
        help="no baixa les dades del drive"
        )

    parser.add_argument(
        dest='date',
        nargs='?',
        default=None,
        help='generates the schedule for the week including such date',
        )

    parser.add_argument(
        '--certificate','-C',
        metavar='CERTIFICATE.json',
        default='drive-certificate.json',
        help='certificat amb permisos per accedir al document gdrive',
        )

    parser.add_argument(
        '--holidays',
        default='odoo',
        choices='drive notoi odoo'.split(),
        help="Origen d'on agafa les vacances",
    )

    parser.add_argument(
        '--drive-file',
        help="Document del drive origen de dades externes"
        )

    parser.add_argument(
        '--config-file',
        default='config.yaml',
        help="fitxer de configuració principal",
    )

    parser.add_argument(
        '--personsfile',
        default='persons.yaml',
        help="fitxer de configuració de les persones",
    )

    parser.add_argument(
        '--idealshifts',
        default=None,
        help="fitxer yaml amb la càrrega ideal de cada persona, si s'especifica aqui no es baixarà",
    )

    parser.add_argument(
        '--weekshifts',
        default=None,
        help="fitxer yaml de sortida amb la càrrega final de cada persona",
    )

    parser.add_argument(
        '--overload',
        default=None,
        help="fitxer yaml de sortida amb la sobrecàrrega final sobre l'ideal ponderat de cada persona",
    )


    return parser.parse_args()

args=None

def main():
    from tomatic.retriever import (
        downloadPersons,
        downloadLeaves,
        downloadIdealLoad,
        downloadVacations,
        downloadFestivities,
        downloadBusy,
        downloadShiftCredit,
        downloadShiftload,
        downloadOverload,
        addDays,
    )

    global args

    args = parseArgs()

    step('Carregant configuració {}...', args.config_file)
    try:
        config = ns.load(args.config_file)
    except:
        error("Configuració incorrecta")
        raise

    if args.date is not None:
        # take the monday of the week including that date
        givenDate = Date(args.date)
        config.monday = addDays(givenDate, - givenDate.weekday())
    else:
        # If no date provided, take the next monday
        today = Date.today()
        config.monday = addDays(today, 7-today.weekday())

    if args.drive_file:
        config.documentDrive = args.drive_file

    if args.personsfile:
        config.personsfile = args.personsfile

    config.idealshifts = config.get('idealshifts') or args.idealshifts or 'idealshifts.csv'

    step("Baixant persones del tomatic...")
    downloadPersons(config)

    if args.personsfile and Path(args.personsfile).exists():
        config.update(ns.load(args.personsfile))

    step("Baixant persones de baixa del drive...")
    config.driveCertificate = args.certificate
    downloadLeaves(config, args.certificate)

    downloadIdealLoad(config, args.certificate)
    downloadBusy(config)
    downloadFestivities(config)
    downloadVacations(config, source='odoo')
    #downloadVacations(config, source='drive')
    #downloadVacations(config, source='notoi')

    step("Baixant bossa d'hores del tomatic...")
    downloadShiftCredit(config)

if __name__ == '__main__':
    main()
