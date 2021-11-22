#!/bin/bash


creditfile=$(ls graelles/shiftcredit-*.yaml | sort | tail -n1)
backupfile="$(dirname $creditfile)/backups/$(basename $creditfile .yaml)-$(date -Iseconds).yaml"

echo "Creating backup $backupfile"
cp "$creditfile" "$backupfile"
echo "Creating an empty $creditfile"
echo "{}" > "$creditfile"






