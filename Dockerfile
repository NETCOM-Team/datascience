FROM python:latest
ENV PYTHONUNBUFFERED 0
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379

LABEL maintainer="rmccarth@andrew.cmu.edu"

RUN mkdir ASN && mkdir data && mkdir master
RUN apt-get update -y && apt-get install -y --no-install-recommends inotify-tools
RUN echo "root" >> /etc/incron.allow

COPY ["./geolite.csv", "data/"]
COPY ["./driver.py", "${APPROOT}"]
COPY ["./s3-job.sh", "${APPROOT}"]
COPY ["./trigger.sh", "${APPROOT}"]
COPY ["ASN", "ASN/"]
COPY ["./requirements.txt", "${APPROOT}"]

RUN pip3 install --upgrade setuptools pip && pip3 install -r requirements.txt
RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
&& unzip awscliv2.zip && ./aws/install


RUN chmod a+x ${APPROOT}/${APP} && chmod +x s3-job.sh && chmod +x driver.py && chmod +x trigger.sh


ENTRYPOINT ["./s3-job.sh"]
