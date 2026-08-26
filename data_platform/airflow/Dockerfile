# syntax=docker/dockerfile:1.7
FROM apache/airflow:slim-3.3.0-python3.12

LABEL maintainer="samanalishiri@gmail.com"

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates wget gpg apt-transport-https \
    && wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public \
        | gpg --dearmor \
        > /etc/apt/trusted.gpg.d/adoptium.gpg \
    && echo "deb https://packages.adoptium.net/artifactory/deb bookworm main" \
        > /etc/apt/sources.list.d/adoptium.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends temurin-21-jre \
    && rm -rf /var/lib/apt/lists/* \
    && JAVA_PATH="$(readlink -f "$(command -v java)")" \
    && ln -s "$(dirname "$(dirname "${JAVA_PATH}")")" /opt/java

ENV JAVA_HOME=/opt/java
ENV PATH="${JAVA_HOME}/bin:/home/airflow/.local/bin:${PATH}"

USER root

RUN mkdir -p /opt/spark-ivy \
    && chown -R airflow:root /opt/spark-ivy

USER airflow

COPY requirements-docker.txt /tmp/requirements.txt

RUN --mount=type=cache,target=/home/airflow/.cache/pip \
    python -m pip install -r /tmp/requirements.txt \
    && java -version \
    && test -x "${JAVA_HOME}/bin/java"

RUN spark-submit \
        --packages "org.postgresql:postgresql:42.7.7,org.apache.hadoop:hadoop-aws:3.4.2,org.slf4j:slf4j-api:1.7.36,org.slf4j:slf4j-reload4j:1.7.36,ch.qos.reload4j:reload4j:1.2.22,org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.2" \
        --conf spark.jars.ivy=/opt/spark-ivy \
        --conf spark.jars.excludes=org.slf4j:slf4j-api \
        --version \
    && chmod -R a+rX /opt/spark-ivy
