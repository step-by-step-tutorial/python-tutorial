# syntax=docker/dockerfile:1.7
FROM spark:4.1.2-java21
LABEL maintainer="samanalishiri@gmail.com"

USER root

ARG PYTHON_VERSION=3.12.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    build-essential \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    uuid-dev \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" -o /tmp/python.tgz \
  && tar -xzf /tmp/python.tgz -C /tmp \
  && cd "/tmp/Python-${PYTHON_VERSION}" \
  && ./configure --enable-optimizations --with-ensurepip=install \
  && make -j"$(nproc)" \
  && make altinstall \
  && ln -sf /usr/local/bin/python3.12 /usr/local/bin/python \
  && ln -sf /usr/local/bin/pip3.12 /usr/local/bin/pip \
  && python --version \
  && pip --version \
  && rm -rf /tmp/python.tgz "/tmp/Python-${PYTHON_VERSION}"

RUN python -m venv /opt/venv && /opt/venv/bin/pip --version

RUN mkdir -p /opt/spark-ivy \
  && /opt/spark/bin/spark-submit \
      --packages "org.postgresql:postgresql:42.7.7,org.apache.hadoop:hadoop-aws:3.4.2,org.slf4j:slf4j-api:1.7.36,org.slf4j:slf4j-reload4j:1.7.36,ch.qos.reload4j:reload4j:1.2.22,org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.2" \
      --conf spark.jars.ivy=/opt/spark-ivy \
      --conf spark.jars.excludes=org.slf4j:slf4j-api \
      --version \
  && chmod -R a+rX /opt/spark-ivy

ENV PATH="/opt/venv/bin:/usr/local/bin:${PATH}" \
    PYSPARK_PYTHON="/usr/local/bin/python" \
    PYSPARK_DRIVER_PYTHON="/usr/local/bin/python"

USER 185
