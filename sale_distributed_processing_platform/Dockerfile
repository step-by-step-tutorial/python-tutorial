FROM python:3.12-slim-trixie
LABEL authors="samanalishiri@gmail.com"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        openjdk-21-jre-headless \
    && JAVA_HOME_PATH="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")" \
    && ln -s "${JAVA_HOME_PATH}" /opt/java \
    && java -version \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/opt/java
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-docker.txt ./requirements.txt
COPY pyproject.toml .
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python -m main && tail -f /dev/null"]
