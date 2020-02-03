#!/bin/bash

#bucketname = netcomdsd

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.
mkdir data
mkdir output

#copy all files from s3 data store to local directory
aws2 s3 cp s3://netcomdsd data/

#invoke combination script that combines all files in data/ and outputs the merged file into output/
./Deepsight_Aggregator.py

#We now have a MASTER.csv aggregate file built in output/
#copy the file to our S3 bucket

aws2 s3 cp output/MASTER.csv s3://netcomdsd


