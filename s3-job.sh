#!/bin/bash

#new s3-job.sh

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.
mkdir data
mkdir master

BUCKET_NAME=analytics-pipeline-cmucybercom
REGION=us-east-1
ACCOUNT_ID=444558491062
aws_access_key_id=AKIAIIBY4MJHF7F4VO4Q
aws_secret_access_key=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

echo $BUCKET_NAME
echo $REGION
echo $ACCOUNT_ID
echo $aws_access_key_id
echo $aws_secret_access_key

echo "above is for debug"

#set our aws credentials

aws configure set aws_access_key_id $aws_access_key_id
aws configure set aws_secret_access_key $aws_secret_access_key


#initially copy our s3 data to local
aws s3 cp s3://$BUCKET_NAME data/  --recursive

./driver.py

aws s3 cp master/MASTER.csv s3://$BUCKET_NAME


#infinite loop to monitor the status of the s3 bucket and trigger quicksight updates upon changes
while true;
  do
    aws s3 sync s3://$BUCKET_NAME data/

    ./driver.py

    aws s3 cp master/MASTER.csv s3://$BUCKET_NAME

  done
