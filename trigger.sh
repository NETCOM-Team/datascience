#!/bin/bash



while true
do
    #watches the data directory for updates from aws s3 sync in the s3-job.sh
    inotifywait -e create data/
    echo "inotify exited, moving onto calling driver.py"
    #when inotifywait triggers, call our driver.py to compile updates in data/
    ./driver.py && echo "this line calls driver directly"
    echo "driver exited"
    #driver.py outputs a MASTER.csv file of compiled threat intel feeds to the master/ directory
    aws s3 cp master/MASTER.csv s3://$BUCKET_NAME
    aws s3 cp master/ASN_Scores.csv s3://$BUCKET_NAME
done
