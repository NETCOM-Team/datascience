#!/bin/bash

echo $BUCKET_NAME
echo $REGION
echo $ACCOUNT_ID
echo $aws_access_key_id
echo $aws_secret_access_key
echo "above is debug"

echo "[default]" > /root/.aws/credentials \
&& echo "aws_access_key_id = $aws_access_key_id" >> /root/.aws/credentials \
&& echo "aws_secret_access_key = $aws_secret_access_key" >> /root/.aws/credentials

echo "AWS credential FILE: "
echo ""
cat /root/.aws/credentials

#set our random IDs so we don't step on other generated pipelines
ASN_DATA_SOURCE_ID=ASNcmunetcom$RANDOM
ASN_DATA_SET_ID=ASNcmunetcoms20$RANDOM
CLEAN_DATA_SOURCE_ID=CLEANcmunetcom$RANDOM
CLEAN_DATA_SET_ID=CLEANcmunetcoms20$RANDOM

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.
mkdir data
mkdir output_initial
mkdir updated
mkdir output_sync

#copy all files from s3 data store to local directory
aws2 s3 cp s3://$BUCKET_NAME data/ --recursive
echo "debug data from s3"
ls data/

#invoke combination script that combines all files in data/ and outputs the merged file into output_initial/
./Aggregating_Deepsight.py
echo "debug data in output_intitial"
ls output_initial/
#We now have a CLEANED.csv aggregate file built in output_initial/

#copy the file to the S3 bucket and QuickSight

aws2 s3 cp output_initial/output_MASTER.csv s3://$BUCKET_NAME



#BUILD connection.json for establish our quicksight -> s3 create-data-source
cat > asn-connection.json <<- EOF

{
    "AwsAccountId": "$ACCOUNT_ID",
    "DataSourceId": "$ASN_DATA_SOURCE_ID",
    "Name": "cmunetcoms20-ASNSource",
    "Type": "S3",
    "DataSourceParameters": {
        "S3Parameters": {
            "ManifestFileLocation": {
                "Bucket": "$BUCKET_NAME",
                "Key": "asn-manifest.json"
            }
          }
        }
}
EOF
cat > clean-connection.json <<- EOF
{
    "AwsAccountId": "$ACCOUNT_ID",
    "DataSourceId": "$CLEAN_DATA_SOURCE_ID",
    "Name": "cmunetcoms20-cleanSource",
    "Type": "S3",
    "DataSourceParameters": {
        "S3Parameters": {
            "ManifestFileLocation": {
                "Bucket": "$BUCKET_NAME",
                "Key": "clean-manifest.json"
            }
          }
        }
}
EOF

#BUILD clean-manifest.json for quicksight ingestion capability. Needs to be uploaded into our s3 bucket.

cat > clean-manifest.json <<- EOF
{
    "fileLocations": [
        {
            "URIs": [
                "https://$BUCKET_NAME.s3.$REGION.amazonaws.com/MASTER.csv"
            ]
        },
        {
            "URIPrefixes": [
                "prefix1",
                "prefix2",
                "prefix3"
            ]
        }
    ],
    "globalUploadSettings": {
        "format": "CSV",
        "delimiter": ",",
        "textqualifier": "'",
        "containsHeader": "true"
    }
}
EOF

cat > asn-manifest.json <<- EOF
{
    "fileLocations": [
        {
            "URIs": [
                "https://$BUCKET_NAME.s3.$REGION.amazonaws.com/ASN_Scores.csv"
            ]
        },
        {
            "URIPrefixes": [
                "prefix1",
                "prefix2",
                "prefix3"
            ]
        }
    ],
    "globalUploadSettings": {
        "format": "CSV",
        "delimiter": ",",
        "textqualifier": "'",
        "containsHeader": "true"
    }
}
EOF

#copy our manifest files into our s3 bucket
aws2 s3 cp clean-manifest.json s3://$BUCKET_NAME
aws2 s3 cp asn-manifest.json s3://$BUCKET_NAME

#generates data-source for integration between quicksight and s3
#connection.json should be built during docker-compose
aws2 configure set REGION $REGION
#create our data sources and save the ARN identifiers in their respective objects
asn_ARN=$(aws2 quicksight create-data-source --cli-input-json file://asn-connection.json | grep "Arn" | awk '{print $2}' | sed 's/\"//g' | sed 's/,//')
clean_ARN=$(aws2 quicksight create-data-source --cli-input-json file://clean-connection.json | grep "Arn" | awk '{print $2}' | sed 's/\"//g' | sed 's/,//')

#BUILD tablemapping for create-data-set; specifies the schema and data types included in the CSV

cat > asn-tablemap <<- EOF
{
    "AwsAccountId": "$ACCOUNT_ID",
    "DataSetId": "$ASN_DATA_SET_ID",
    "Name": "asn-tablemapping",
    "PhysicalTableMap": {
        "ASNs": {
            "S3Source": {
                "DataSourceArn": "$asn_ARN",
                "UploadSettings": {
                "Format": "XLSX",
                "StartFromRow": 1,
                "ContainsHeader": true,
                "TextQualifier": "DOUBLE_QUOTE",
                "Delimiter": ","
                },
                "InputColumns": [
                {
                "Name": "ASN",
                "Type": "STRING"
                },
                {
                "Name": "Score",
                "Type": "STRING"
                },
                {
                "Name": "Total_IPs",
                "Type": "STRING"
                },
                {
                "Name": "Badness",
                "Type": "STRING"
                }
                ]
            }
      }
    },
    "ImportMode": "SPICE"
}
EOF

cat > clean-tablemap <<- EOF
{
    "AwsAccountId": "$ACCOUNT_ID",
    "DataSetId": "$CLEAN_DATA_SET_ID",
    "Name": "clean-tablemapping",
    "PhysicalTableMap": {
        "ASNs": {
            "S3Source": {
                "DataSourceArn": "$asn_ARN",
                "UploadSettings": {
                "Format": "XLSX",
                "StartFromRow": 1,
                "ContainsHeader": true,
                "TextQualifier": "DOUBLE_QUOTE",
                "Delimiter": ","
                },
                "InputColumns": [
                {
                "Name": "ASN",
                "Type": "STRING"
                },
                {
                "Name": "Score",
                "Type": "STRING"
                },
                {
                "Name": "Total_IPs",
                "Type": "STRING"
                },
                {
                "Name": "Badness",
                "Type": "STRING"
                }
                ]
            }
      }
    },
    "ImportMode": "SPICE"
}
EOF

#create the data sets
aws2 quicksight create-data-set --cli-input-json file://asn-tablemap
aws2 quicksight create-data-set --cli-input-json file://clean-tablemap

#infinite loop to monitor the status of the s3 bucket and trigger quicksight updates upon changes
#while true
#do
#    aws2 s3 sync s3://$BUCKET_NAME output_sync/ --exclude asn-manifest.json --exclude clean-manifest.json
#    ./placeholder.py  # should read in the files and compile them into a new master list and write it to updated/
#    aws2 s3 cp updated/MASTER.csv s3://$BUCKET_NAME

    #next 2 lines need testing for functionality before deployment, need to construct json inputs appropriately
#    aws2 quicksight update-data-set --cli-input-json file://asn-update-tablemap
#    aws2 quicksight update-data-set --cli-input-json file://clean-update-tablemap


    #do we ever have a case where we need to break out of this? error handling?
#done
