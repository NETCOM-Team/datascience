#!/bin/bash

#new s3-job.sh

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.
mkdir data
mkdir master



#initially copy our s3 data to local
aws s3 cp s3://$BUCKET_NAME data/  --recursive

./driver.py

aws s3 cp master/MASTER.csv s3://$BUCKET_NAME


#infinite loop to monitor the status of the s3 bucket and trigger quicksight updates upon changes
while:
  do
    aws s3 sync s3://$BUCKET_NAME data/

    ./driver.py

    aws s3 cp master/MASTER.csv s3://$BUCKET_NAME

  done
