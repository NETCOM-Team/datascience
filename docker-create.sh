#!/bin/bash

cp ~/.aws/credentials .

docker image build --tag python-test:auto .
