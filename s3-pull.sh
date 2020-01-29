#!/bin/bash

#bucketname = netcomdsd
#configure AWS keys through aws configure in command line prior to running the script

#make directory to store our bucket files locally
mkdir data


#copy all files from s3 data store to local directory
#aws s3 cp s3://netcomdsd/ data/ --recursive


#invoke "trimming" script to remove unwanted columns from the csv files that were pulled


FILES="data/*"

#progress bar setup

sp="/-\|"
sc=0
spin() {
  	printf "\b${sp:sc++:1}"
	((sc==${#sp})) && sc=0
}

endspin() {
	printf "\r%s\n" "$@"
}

#for file in our data directory process each file with our python script
for file in $FILES
do
	spin	
	basename $file | ./doNothing.py

done
endspin

