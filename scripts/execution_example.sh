#!/bin/bash

# This script is useful to test execution_api.py
# It simulates a long task which listens to SIGINT
# in order to stop gracefully.


stopped=0
function stop() {
	stopped=1
}
function ignore() {
 	false
	echo "SIGHUP!!"
}
trap 'stop' SIGINT
trap 'ignore' SIGHUP # Avoid stop on parent process detach

echo Current path: $(pwd)
echo This is an error message >&2
echo PID: $$

echo "Esperando 10s para poderse interrumpir"
for a in 10 9 8 7 6 5 4 3 2 1 0; do
	sleep 1
	echo $a
done
echo "El proceso tardara 100s, ya se puede interrumpir"
for ((a=0; a<100; a++)); do
	[ "$stopped" == 1 ] && {
		echo Stopping
		break
	}
	sleep 1
	echo $a
done
echo "Finito" $stopped

