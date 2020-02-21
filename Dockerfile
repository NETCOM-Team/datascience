FROM python:latest
ENV PYTHONUNBUFFERED 0
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379

LABEL maintainer="rmccarth@andrew.cmu.edu"

RUN mkdir ASN && mkdir data && mkdir master

COPY ["./geolite.csv", "data/"]
COPY ["./driver.py", "${APPROOT}"]
COPY ["./s3-job.sh", "${APPROOT}"]
COPY ["ASN", "ASN/"]
COPY ["./requirements.txt", "${APPROOT}"]

RUN pip3 install --upgrade setuptools pip
RUN pip3 install -r requirements.txt
RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
&& unzip awscliv2.zip && ./aws/install


RUN chmod a+x ${APPROOT}/${APP}
RUN chmod +x s3-job.sh
RUN chmod +x driver.py

ENTRYPOINT ["./s3-job.sh"]
