#!/bin/bash

if [ $# -eq 1 ]
then
    basepath=$1
else
    basepath=output
fi

PYPATH=python3

iter=-1
odir=$(date +%Y%h%d.%H%M%S)
printf "======== Iteration %03d ========\n" $iter
# Use maximum -m value to exhaust the entire seed file
$PYPATH main.py -s -b "$basepath" -d $odir -m 1000

PendingFile="$basepath"/$odir/pending_titles.txt
while [ -s  "$PendingFile" ]
do
    iter=$((iter+1))
    printf "======== Iteration %03d ========\n" $iter
    lines=$(wc -l "$PendingFile")
    echo Pending titles $lines...
    $PYPATH main.py -r -b "$basepath" -d $odir -m 100
done
