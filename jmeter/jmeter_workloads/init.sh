#!/bin/bash

toggle-test.sh $TEST_GROUP true $TEST_PLAN

echo $JHOST $JPORT $JRAMP

jmeter -n \
  -Dprometheus.ip=0.0.0.0 \
  -DusePureIDs=true \
  -t $JMETER_HOME/$TEST_PLAN \
  -JTOPUID=$JTOPUID \
  -JHOST=$JHOST \
  -JPORT=$JPORT \
  -JTHREADS=$JTHREADS \
  -JRATIO=$JRATIO \
  -JTHROUGHPUT=$JTHROUGHPUT \
  -JSTEPTHREADS=$JSTEPTHREADS \
  -JRAMP=$JRAMP \
  -JMAXTHINKTIME=$JMAXTHINKTIME \
  -JSTOCKS=$JSTOCKS \
  -JDURATION=$JDURATION \
  -JQUOTES=$JQUOTES \
  -JSELLS=$JSELLS \
  -JBUYS=$JBUYS \
  -JWAIT_RESP=$JWAIT_RESP \
  -JTARGET_THROUGHPUT=$JTARGET_THROUGHPUT

