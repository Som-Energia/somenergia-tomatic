#!/usr/bin/env python

import sys
from tomatic.shiftload import loadSum, loadMin, loadSubstract
from yamlns import namespace as ns

def main():
    if sys.argv[1] == 'min':
        result = loadMin(*(
            ns.load(filename)
            for filename in sys.argv[2:]
        ))
    elif sys.argv[1] == 'subs':
        result = loadSubstract(*(
            ns.load(filename)
            for filename in sys.argv[2:4]
        ))
    else:
        result = loadSum(*(
            ns.load(filename)
            for filename in sys.argv[1:]
        ))

    result = ns((p,round(v,1)) for p,v in sorted(result.items()))
    print(result.dump())

if __name__ == "__main__":
    main()

# vim: et ts=4 sw=4
