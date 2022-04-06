#!/bin/bash

first=$(date -I -d "${1:-$(date -I)}")
last=$(date -I -d "${2:-$1}")
date="$first"
echo "From $first to $last, both included"
mkdir -p dump_stats/
while true
do
	echo "$date"
	areavoip_callapi.py INFO info simplecdrs start "$date 00:00:00" end "$date 23:59:59" format json secondsTimeout 20 > "dump_stats/simple_cdrs-$date.yaml"
	areavoip_callapi.py INFO info simplecdrs start "$date 00:00:00" end "$date 23:59:59" format csv  secondsTimeout 20 > "dump_stats/simple_cdrs-$date.csv"
	areavoip_callapi.py INFO info cdrs start "$date 00:00:00" end "$date 23:59:59" format json secondsTimeout 20 > "dump_stats/cdrs-$date.yaml"
	areavoip_callapi.py INFO info cdrs start "$date 00:00:00" end "$date 23:59:59" format csv  secondsTimeout 20 > "dump_stats/cdrs-$date.csv"
	tomatic_dailyreport.py stats --backend areavoip --date $date
	[[ "$date" < "$last" ]] || exit
	date=$(date -I -d "$date+1day")
done

