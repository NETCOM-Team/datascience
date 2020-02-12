FROM python:latest
LABEL maintainer="rmccarth@andrew.cmu.edu"

RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
&& unzip awscliv2.zip \
&& ./aws/install

COPY ["./placeholder.py", "${APPROOT}"]
COPY ["./s3-job.sh", "${APPROOT}"]
COPY ["./Deepsight_Aggregator.py", "${APPROOT}"]
COPY ["./requirements.txt", "${APPROOT}"]
RUN pip3 install -r requirements.txt


ARG aws_access_key_id=default
ENV aws_key_id=$aws_access_key_id
ARG aws_secret_access_key=default
ENV aws_secret_key=${aws_secret_access_key}

RUN mkdir /root/.aws && echo "[default]" > /root/.aws/credentials \
&& echo "aws_access_key_id = $aws_key_id" >> /root/.aws/credentials \
&& echo "aws_secret_access_key = $aws_secret_access_key" >> /root/.aws/credentials

RUN chmod a+x ${APPROOT}/${APP}

ENTRYPOINT ["./s3-job.sh"]




