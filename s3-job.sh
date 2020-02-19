#!/bin/bash

#new s3-job.sh

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.

aws configure set aws_access_key_id $aws_access_key_id
aws configure set aws_secret_access_key $aws_secret_access_key


#initially copy our s3 data to local
aws s3 cp s3://$BUCKET_NAME data/  --recursive --exclude MASTER.csv

./driver.py

aws s3 cp master/MASTER.csv s3://$BUCKET_NAME

#infinite loop to monitor the status of the s3 bucket and trigger quicksight updates upon changes
#while true;
#  do
    # keep the data/ dir up to date with what exists in s3; ignoring MASTER.csv since we plan on overwriting this
    # file as new threat intel feeds get added to s3. 
#    aws s3 sync s3://$BUCKET_NAME data/ --exclude MASTER.csv

    # run driver.py again to output MASTER.csv to master/
#    ./driver.py

    # upload MASTER.csv to our s3 bucket for use with quicksight. 
    aws s3 cp master/MASTER.csv s3://$BUCKET_NAME

#  done

