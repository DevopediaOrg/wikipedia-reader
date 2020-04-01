#!/bin/bash

iter=0
odir=$(date -u +%Y%h%d.%H%M%S)
printf "======== Iteration %03d ========\n" $iter
python3 main.py -r -d $odir

PendingFile=data/pending_titles.txt
while [ -s  $PendingFile ]
do
    iter=$((iter+1))
    printf "======== Iteration %03d ========\n" $iter
    lines=$(wc -l $PendingFile)
    echo Pending titles $lines...
    python3 main.py -p -r -d $odir
done
