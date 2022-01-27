#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import dbconfig
import erppeek
import os
import datetime
from yamlns.dateutils import Date
from tomatic.callregistry import CallRegistry


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'date',
        nargs='?',
        type=Date,
        help="Data dels casos que es volen pujar"
    )
    args = parser.parse_args()

    today = args.date or datetime.date.today()

    erp = erppeek.Client(**dbconfig.erppeek)
    CallRegistry().uploadCases(erp, today)


# vim: et ts=4 sw=4
