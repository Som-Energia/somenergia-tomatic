#!/bin/bash
# HACK to overcome elliot ill python environment

if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(/home/somenergia/.pyenv/bin/pyenv init -)"
fi
/home/somenergia/.pyenv/bin/pyenv local 3.8.5
/home/somenergia/.pyenv/shims/python3 ./tomatic_says.py "$@"
/home/somenergia/.pyenv/bin/pyenv local --unset

