#!/bin/bash

BUCKET_NAME="analytics-pipeline-cmucybercom" 
REGION="us-east-1"
ACCOUNT_ID="444558491062"
ASN_DATA_SOURCE_ID=ASNcmunetcom$RANDOM
ASN_DATA_SET_ID=ASNcmunetcoms20$RANDOM
CLEAN_DATA_SOURCE_ID=CLEANcmunetcom$RANDOM
CLEAN_DATA_SET_ID=CLEANcmunetcoms20$RANDOM

#make directory to store our bucket files locally; make directory to save our MASTER.csv merge-file.
mkdir data
mkdir output_initial
mkdir updated/
mkdir output_sync

#copy all files from s3 data store to local directory
aws2 s3 cp s3://$BUCKET_NAME data/

#invoke combination script that combines all files in data/ and outputs the merged file into output_initial/
./Deepsight_Aggregator.py

#We now have a CLEANED.csv aggregate file built in output_initial/

#copy the file to the S3 bucket and QuickSight 

aws2 s3 cp output_initial/MASTER.csv s3://$BUCKET_NAME



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

