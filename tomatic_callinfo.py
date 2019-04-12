#!/usr/bin/env python


from tomatic.callinfo import CallInfo

import dbconfig
import erppeek
import sys

O = erppeek.Client(**dbconfig.erppeek)
callinfo = CallInfo(O)
print callinfo.getByPhone(sys.argv[1]).dump()





