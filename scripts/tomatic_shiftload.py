#!/usr/bin/env python

from tomatic import scenario_config
from tomatic import shiftload

if __name__ == '__main__':
    args = scenario_config.parseArgs()
    shiftload.main(args)


