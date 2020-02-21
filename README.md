# Deployment

Note: Requires you to have **docker desktop** installed on your system.

```bash
git clone https://github.com/cmunetcoms20/datascience.git
cd datascience/
```
Add your bucket name, aws account id number, aws_access_key_id, and aws_secret_access_key to the .env_template included in the project; rename .env_template to .env. 

Then run:  

```bash
docker-compose up
```

To destroy the environment simply run:  

```bash
docker-compose down
```

After making custom changes/alterations to the build images or scripts run:  
```bash 
docker-compose up --build
```
To execute a build without relying on cached docker objects.  

## Django API

An API is now exposed to the host on port 8000 and included in the docker-compose environment. The API is still in development and requires further development. 
```
Access the API by navigating to 127.0.0.1:8000/api/ in your browser or executing:  
```bash
curl 127.0.0.1:8000/api/
```
The API endpoint GET /api currently returns a JSON object of the first 100 ASN objects and their respective risk scores. To query the score of a particular ASN:

```bash
curl 127.0.0.1:8000/api/ | jq .'4444'
```

# Functionality

The environment will deploy a python app container and a Redis container. The python application will pull down the .csv files located in your s3 bucket and merge them into a MASTER.csv file, re-uploading to the s3 bucket when complete.  

The environment will then monitor the s3 bucket for any future s3 files, rebuilding the MASTER.csv file and re-uploading a freshly-compiled version when applicable. 

The environment generates key-value pairs of the format ASN:risk_score and stores them in Redis for fast-lookups. 

# Planned Development. 

[Proof of Concept COMPLETED] Plans for further development include deploying a Django API to provide query-capability to the ASN objects stored in Redis. 

Additional plans include the development of a console application which will allow technically-capable operators to generate on-the-fly descriptive metrics of the ASN threat-landscape described by the data indexed in Redis in quasi-realtime.  





