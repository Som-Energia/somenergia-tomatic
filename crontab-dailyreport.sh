#!/bin/bash

PYTHONIOENCODING=utf8 ./tomatic_calls.py summary | while read a; do ./tomatic_says.py "$a"; done


