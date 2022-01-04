#!/bin/bash

export PYTHONIOENCODING=utf8

missatge="$(
    echo "Ei Supers! Ja hem tancat telèfons!"
    echo "Gràcies per la feina feta!"
#  tomatic_calls.py summary
)"
tomatic_says.py "$missatge"
tomatic_dailyreport.py

