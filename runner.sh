#!/bin/bash

if [ $# -eq 1 ]
then
    basepath=$1
else
    basepath=output
fi

iter=0
odir=$(date +%Y%h%d.%H%M%S)
printf "======== Iteration %03d ========\n" $iter
# Use maximum -m value to exhaust the entire seed file
python main.py -s -b $basepath -d $odir -m 10

PendingFile=$basepath/$odir/pending_titles.txt
while [ -s  $PendingFile ]
do
    iter=$((iter+1))
    printf "======== Iteration %03d ========\n" $iter
    lines=$(wc -l $PendingFile)
    echo Pending titles $lines...
    python main.py -r -b $basepath -d $odir -m 10
done
