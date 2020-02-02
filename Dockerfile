FROM python:latest
LABEL maintainer="rmccarth@andrew.cmu.edu"

RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
&& unzip awscliv2.zip \
&& ./aws/install

COPY ["./s3-job.sh", "${APPROOT}"]
COPY ["./Deepsight_Aggregator.py", "${APPROOT}"]
COPY ["./requirements.txt", "${APPROOT}"]


ARG aws_credential_file=default
ENV env_var_name=$aws_credential_file
COPY ["./credentials", "/root/.aws/credentials"]

RUN chmod a+x ${APPROOT}/${APP}

ENTRYPOINT ["./s3-job.sh"]




