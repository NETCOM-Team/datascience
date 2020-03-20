# Deployment

Note: Requires you to have **docker desktop** installed on your system.

```bash
git clone https://github.com/cmunetcoms20/datascience.git
cd datascience/
```
Add your bucket name, aws account id number, aws_access_key_id, and aws_secret_access_key to the .env_template included in the project; rename .env_template to .env. 

To build the environment:  

```bash
docker-compose up
```
To destroy the environment:  
```bash
docker-compose down
```

After making custom changes/alterations to the build images or scripts run:  
```bash 
docker-compose up --build
```
To execute a build without relying on cached docker objects.  

## Django API

An API is now exposed to the host on port 8000 and included in the docker-compose environment. The API provides a number of endpoints to aid analysts in queries for ASNs or IPs of interest e.g.  

```json
GET /asn

body:
{
	"asn":["17054"]
}

response:  

{
    "asns": [
        {
            "17054": 76.83333333333336
        }
    ]
}
```

The API is documented here: [Datascience API](https://github.com/cmunetcoms20/datascience/wiki/API)  

# Functionality

The environment will deploy a python app container and a Redis container. The python application will pull down the .csv files located in a specified s3 bucket and merge them into a MASTER.csv file, re-uploading to the s3 bucket when complete.  

The environment will then monitor the s3 bucket for any future s3 files, rebuilding the MASTER.csv file and re-uploading a freshly-compiled version when applicable. 

The environment generates key-value pairs of the format ASN:risk_score and stores them in Redis for fast-lookups. 





