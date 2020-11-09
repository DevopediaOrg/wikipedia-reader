#!/bin/bash

PYPATH=python3


if [ $# -eq 1 ]
then
    basepath=$1
else
    basepath=output
fi

if [ $# -eq 2 ]
then
    odir=$2
    printf "======== No Seeding ========\n"
    printf "Continuing from previous crawl in %s...\n" $odir
else
    odir=$(date +%Y%h%d.%H%M%S)
    printf "======== Seeding ========\n"
    printf "Saving new crawl in %s...\n" $odir
    # Use maximum -m value to exhaust the entire seed file
    $PYPATH main.py -s -b "$basepath" -d $odir -m 1000
fi


iter=0
PendingFile="$basepath"/$odir/pending_titles.txt
while [ -s  "$PendingFile" ]
do
    iter=$((iter+1))
    printf "======== Iteration %03d ========\n" $iter
    lines=$(wc -l "$PendingFile")
    echo Pending titles $lines...
    $PYPATH main.py -r -b "$basepath" -d $odir -m 100
    if [ $? -ne 0 ]
    then
        exit
    fi
done
