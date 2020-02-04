# Instructions

Note: Requires you to have **docker desktop** installed on your system.

```bash
git clone https://github.com/cmunetcoms20/datascience.git
cd datascience/
```

Create the docker container like the example below:
```bash
docker image build --tag datascience . --build-arg aws_access_key_id="AKIAYH7A4CIQ" --build-arg aws_secret_access_key="f10Gp040R04ZHIUf8UZ"
```

```bash
docker run datascience
```
The last command will run the docker container that you created and run our application which will pull down your s3 threat intelligence feed csv's and create a MASTER.csv and upload it back into s3 for processing and data exploration.



