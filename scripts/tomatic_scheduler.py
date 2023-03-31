#!/usr/bin/env python

from tomatic.backtracker import main as backtracking
from tomatic.minizinc import main as minizinc


if __name__ == '__main__':
    success = minizinc()
    if not success:
        backtracking()


# vim: noet
