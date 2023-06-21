#!/usr/bin/env python

from tomatic import backtracker
from tomatic import shiftload

if __name__ == '__main__':
    args = backtracker.parseArgs()
    shiftload.main(args)


