FROM python:latest
ENV PYTHONUNBUFFERED 0
ENV REDIS_HOST redis
ENV REDIS_PORT 6379

LABEL maintainer="rmccarth@andrew.cmu.edu"

RUN mkdir ASN && mkdir data && mkdir master
RUN apt-get update -y && apt-get install -y --no-install-recommends inotify-tools
RUN apt install python-setuptools -y
RUN echo "root" >> /etc/incron.allow

COPY ["Data", "data/"]
COPY ["./driver.py", "${APPROOT}"]
COPY ["./s3-job.sh", "${APPROOT}"]
COPY ["./trigger.sh", "${APPROOT}"]
COPY ["./requirements.txt", "${APPROOT}"]

RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python get-pip.py
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

RUN curl -s "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
&& unzip awscliv2.zip && ./aws/install


RUN chmod a+x ${APPROOT}/${APP} && chmod +x s3-job.sh && chmod +x driver.py && chmod +x trigger.sh


ENTRYPOINT ["./s3-job.sh"]
