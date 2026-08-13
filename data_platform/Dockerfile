FROM python:3.12-slim-trixie

LABEL authors="samanalishiri@gmail.com"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates openjdk-21-jre-headless bash \
    && rm -rf /var/lib/apt/lists/* \
    && JAVA_PATH="$(readlink -f "$(command -v java)")" \
    && JAVA_HOME_PATH="$(dirname "$(dirname "${JAVA_PATH}")")" \
    && ln -s "${JAVA_HOME_PATH}" /opt/java

ENV JAVA_HOME=/opt/java
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENV DATASET_NAME=sale
ENV PIPELINE_TYPE=inmemory_auditable

WORKDIR /app

COPY requirements-docker.txt ./requirements.txt
COPY pyproject.toml ./
COPY src ./src
COPY scripts ./scripts

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip install -e .

RUN java -version \
    && test -x "${JAVA_HOME}/bin/java"

CMD ["sh", "-c", "python -m main"]