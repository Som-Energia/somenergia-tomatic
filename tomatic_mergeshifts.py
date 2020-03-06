#!/usr/bin/env python

import sys
from tomatic.shiftload import loadSum
from yamlns import namespace as ns

def main():
    result = loadSum(*(
        ns.load(filename)
        for filename in sys.argv[1:]
    ))
    print(result.dump())

if __name__ == "__main__":
    main()

# vim: et ts=4 sw=4
