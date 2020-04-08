#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import re
from consolemsg import warn, step, error
from datetime import datetime, timedelta
from shutil import copyfile
from pathlib import Path

@click.command()
@click.help_option()

@click.option('--fromdate',
    default=datetime.today().strftime("%Y-%m-%d"),
    help="Choose a monday for computing schedules. Format: YYYY-MM-DD",)
@click.option('--linenumber',
     default=7,
     help="Choose the numer of lines to attend calls")
def tomatic_sandbox(fromdate  ,linenumber):
    try:
        step("Creando sandbox para la graella de la semana {}",fromdate)

        fromdate = datetime.strptime(fromdate, '%Y-%m-%d')
        if not fromdate.weekday() == 0:
            fromdate = fromdate + timedelta(days=-fromdate.weekday(), weeks=1)
        graellaFolder = fromdate.strftime("%Y-%m-%d")

        step("Creando directorio {}", graellaFolder)
        Path(graellaFolder).mkdir()
        linkCertificate = Path(graellaFolder+'/drive-certificate.json')

        step("Creando enlace al certificado {}", linkCertificate)
        linkCertificate.symlink_to('../drive-certificate.json')

        source = Path('config.yaml')
        destination = Path(graellaFolder+'/config.yaml')
        step("Creando fichero {}", source)
        copyfile(source, destination)
        if linenumber:
            step("Añadiendo numero de lineas {} al fichero {}", linenumber, source)
            text = destination.read_text()
            text2fix = re.compile(r'nTelefons: \d+')
            text = text.replace(text2fix.findall(text)[0], "nTelefons: "+str(linenumber))
            destination.write_text(text)
    except Exception as e:
        error(e)
        raise

if __name__ == '__main__':
   tomatic_sandbox()

# vim: et ts=4 sw=4
