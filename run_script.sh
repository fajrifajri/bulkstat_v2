#!/bin/bash

BULKSTAT_DIR=/home/afajri/bulkstat/

inotifywait -m -e create -e moved_to --format "%f" $BULKSTAT_DIR \
        | while read FILENAME
                do
                        echo  processing $BULKSTAT_DIR$FILENAME
			/home/afajri/bulkstat_v2/process_bulkstat.py $BULKSTAT_DIR$FILENAME
                done
