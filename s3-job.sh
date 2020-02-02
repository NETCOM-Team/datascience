#!/bin/bash

#install our required libraries
pip3 install -r requirements.txt

#installing the aws command line interface:

#curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
#unzip awscli-bundle.zip
#sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws

#bucketname = netcomdsd
#configure AWS keys through aws configure in command line prior to running the script

#make directory to store our bucket files locally
mkdir data


#copy all files from s3 data store to local directory
aws s3 cp s3://netcomdsd data/

#invoke combination script that combines all files in Full/ and outputs the merged file into Full/Output/
./Deepsight_Aggregator.py
