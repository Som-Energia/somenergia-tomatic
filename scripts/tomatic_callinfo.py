#!/usr/bin/env python


from __future__ import print_function
from tomatic.callinfo import CallInfo
from tomatic.config import secrets
import erppeek
import sys

O = erppeek.Client(**secrets('erppeek'))
callinfo = CallInfo(O)
print(callinfo.getByPhone(sys.argv[1]).dump())





