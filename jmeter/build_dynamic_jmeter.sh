#!/bin/bash

docker build -f dynamic_jmeter.Dockerfile -t wellisonraul/dynamic_jmeter:0.0.58 .
docker push wellisonraul/dynamic_jmeter:0.0.58
