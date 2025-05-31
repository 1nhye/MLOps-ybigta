FROM confluentinc/cp-kafka-connect:7.5.3

RUN confluent-hub install --no-prompt confluentinc/kafka-connect-s3:10.6.6

COPY connectors /connectors
COPY register-s3.sh /register-s3.sh

USER root
RUN chmod +x /register-s3.sh

