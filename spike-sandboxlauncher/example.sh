#!/bin/bash
stopped=0
function stop() {
	stopped=1
}
function ignore() {
 	false
}
trap 'stop' SIGINT
trap 'ignore' SIGHUP # Avoid stop on parent process detach

echo Current path: $(pwd)
echo PID: $$
echo $$ > pid
echo "Esperando 10s"
for a in 10 9 8 7 6 5 4 3 2 1 0; do
	sleep 1
	echo $a
done
echo "El proceso tardara 100s, se puede interrumpir"
for ((a=0; a<100; a++)); do
	[ "$stopped" == 1 ] && {
		echo Stopping
		break
	}
	sleep 1
	echo $a
done
echo "Finito" $stopped

