#!/bin/bash

export PYTHONIOENCODING=utf8

missatge="$(
    echo "Ei Supers! Ja hem tancat telèfons!"
    ./tomatic_calls.py summary
    echo "Gràcies per la feina feta!"
)"
./tomatic_says.sh "$missatge"


