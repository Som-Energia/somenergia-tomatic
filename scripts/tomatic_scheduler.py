#!/usr/bin/env python

from tomatic.backtracker import main as backtracking
from tomatic.minizinc import main as minizinc
from consolemsg import error

if __name__ == '__main__':
    success = False
    try:
      success = minizinc()
    except:
       error("Minizinc crashed!")
    if not success:
        backtracking()

# vim: noet
