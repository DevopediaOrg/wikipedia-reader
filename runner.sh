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
python3 main.py -r -o $odir

PendingFile=$basepath/$odir/pending_titles.txt
while [ -s  $PendingFile ]
do
    iter=$((iter+1))
    printf "======== Iteration %03d ========\n" $iter
    lines=$(wc -l $PendingFile)
    echo Pending titles $lines...
    python3 main.py -c -r -o $odir
done
