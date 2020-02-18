FROM python:latest
LABEL maintainer="rmccarth@andrew.cmu.edu"

RUN mkdir ASN

COPY ["./driver.py", "${APPROOT}"]
COPY ["./s3-job.sh", "${APPROOT}"]
COPY ["ASN", "ASN/"]
COPY ["./requirements.txt", "${APPROOT}"]

RUN cat requirements.txt

RUN pip3 install --upgrade setuptools pip
RUN pip3 install -r requirements.txt
RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
&& unzip awscliv2.zip && ./aws/install


RUN chmod a+x ${APPROOT}/${APP}
RUN chmod +x s3-job.sh
RUN chmod +x driver.py 
RUN ls -al ${APPDATA}
RUN ls -al ASN/

ENTRYPOINT ["./s3-job.sh"]




