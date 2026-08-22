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

USER airflow

COPY requirements-docker.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && java -version \
    && test -x "${JAVA_HOME}/bin/java"
