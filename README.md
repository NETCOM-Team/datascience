# Instructions

Note: Requires you to have docker installed on your system and valid s3 bucket keys installed in their default location (~/.aws/) on your host.

```bash
git clone https://github.com/cmunetcoms20/datascience.git
cd datascience/
```
```bash
chmod +x docker-create.sh && ./docker-create.sh
```

```bash
docker run python-test:auto
```

The last command will run the docker container that you created and run our application which will pull down your s3 threat intelligence feed csv's and create a MASTER.csv and upload it back into s3 for processing and data exploration.



