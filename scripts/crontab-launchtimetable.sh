#!/bin/bash

weeksInAdvance=2
week=$(date +%F -d "next Monday + $weeksInAdvance weeks")
tomatic_timetablelauncher.py $week

