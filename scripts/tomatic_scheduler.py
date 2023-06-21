#!/usr/bin/env python

from tomatic import backtracker
from tomatic import minizinc
from consolemsg import error, step
import traceback

def main():
    args = backtracker.parseArgs()
    solvers = [
        minizinc,
        backtracker,
    ]
    if args.scheduler == 'backtracker':
        solvers = solvers[::-1]

    for solver in solvers:
        step("Running solver {}", solver.__name__)
        try:
            solver.main(args)
            return
        except Exception as e:
            error("Solver {} crashed", solver.__name__)
            error(traceback.format_exc())

if __name__ == '__main__':
    main()

# vim: noet
