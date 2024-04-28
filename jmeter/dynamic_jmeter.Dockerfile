# Dockerfile to build a jmeter container able to drive acmeair
# Results appear on /output in the container
# Must specify the hostname for the acmeair application (or localhost will be assumed)
FROM wellisonraul/jmeter_plain:0.2

# Copy the script to be executed and other needed files
COPY jmeter_workloads/toggle-test.sh $JMETER_HOME/bin/toggle-test.sh
COPY jmeter_workloads/init.sh $JMETER_HOME/bin/init.sh
RUN chmod a+x $JMETER_HOME/bin/init.sh

# Environment variables that we want the user to redefine
ENV JTOPUID=499 

EXPOSE 9270

COPY jmeter_workloads/. $JMETER_HOME/

ENTRYPOINT ["/bin/bash",  "-c", "init.sh"]


