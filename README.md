# Deployment

Note: Requires you to have **docker desktop** and **docker-compose** installed on your system.

__Ensure that TCP port 8000 is exposed for external systems to query the API__

Run the following:  

```bash
git clone https://github.com/cmunetcoms20/datascience.git
cd datascience/
```
Add your bucket name, aws account id number, aws_access_key_id, and aws_secret_access_key to the .env_template included in the project; rename .env_template to .env. 

Example .env file:

```bash
#the name of S3 bucket where threat intelligence feeds are stored
BUCKET_NAME=threat-intelligence-feed-bucket
#the region of your S3 bucket
REGION=us-east-1
ACCOUNT_ID=444558412345
aws_access_key_id=AKIAIIBY4JHILKMNOPQ
aws_secret_access_key=oMXJicweRuMKhTBmmDBJIHLjkljHASFAj
```  

To build the environment on CentOS, RHEL, Debian, or macOS:  

```bash
sysctl vm.overcommit_memory=1
docker-compose up
```
To destroy the environment:  
```bash
docker-compose down
```
* On Debian you may need to run docker-compose with "sudo"

After making custom changes/alterations to the build images or scripts run:  
```bash 
docker-compose up --build
```
To execute a build without relying on cached docker objects.  

To fully destroy all containers and cached components:  

```bash
docker system prune -a
```
To persist the application stack beyond an SSH session - one may choose to run the application stack as a service on the system, or in a screen session. We found screen to be reliable, however perhaps not the most robust for long-term deployments. 

To use screen, start by running screen before executing docker-compose up. To then detach the screen and keep the stack running after exit, hold ctrl - a, and then press d.  

## Django API

An API is automatically made available on port 8000. The API provides a number of endpoints to aid analysts in queries for ASNs or IPs of interest e.g.  

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

Native visualizations are provided within the python "app" container and can be extracted as-needed:  

```bash
docker cp app:/file/path/within/container /host/path/target
```
Do make sure that the visualizations functions are uncommented in the source code. Then you can run something like;
```bash 
docker cp app:datascience/top_10.pdf /path/to/save/file/to
docker cp app:datascience/fast_mover.pdf /path/to/save/file/to
```

![image](https://imgur.com/CLCj35z.jpg)

A demonstration of the application stack being deployed:

https://asciinema.org/a/L5c49gSQMjyNhRqjoUEkcrGUn



