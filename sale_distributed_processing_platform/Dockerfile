FROM python:3.12-slim-trixie

LABEL authors="samanalishiri@gmail.com"

ENV JAVA_HOME=/opt/java \
    PATH="/opt/java/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        openjdk-21-jre-headless \
    && JAVA_HOME_PATH="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")" \
    && ln -s "${JAVA_HOME_PATH}" "${JAVA_HOME}" \
    && java -version \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-docker.txt ./requirements.txt
COPY pyproject.toml ./
COPY src ./src
COPY scripts ./scripts

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-deps .

CMD ["sh", "-c", "python -m main && tail -f /dev/null"]
