# syntax=docker/dockerfile:1.7
FROM python:3.12-slim-trixie

LABEL authors="samanalishiri@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app
ENV CONFIG_DIR=/app/config
ENV OUTPUT_DIR=/app/output

WORKDIR /app

COPY pyproject.toml ./
COPY requirements.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY src ./src
COPY config ./config
COPY data ./data
COPY scripts ./scripts

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install .

CMD ["python", "-m", "test_data"]
