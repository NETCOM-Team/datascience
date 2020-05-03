#!/bin/bash
su root

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.

aws configure set aws_access_key_id $aws_access_key_id
aws configure set aws_secret_access_key $aws_secret_access_key

# run our trigger script in the background to listen for any changes to the data/ directory
aws s3 cp s3://$BUCKET_NAME data/ --exclude MASTER.csv --exclude ASN_Scores.csv --exclude clean-manifest.json --exclude asn-manifest.json --exclude dashboard_testing*.csv
./trigger.sh &

while true
do
    aws s3 sync s3://$BUCKET_NAME data/ --exclude MASTER*.csv --exclude ASN_Scores.csv --exclude clean-manifest.json --exclude asn-manifest.json --exclude dashboard_testing*.csv --exclude ASN_Scores*.csv --exclude random-manifest.json
done






