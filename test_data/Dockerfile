FROM python:3.12-slim-trixie

LABEL authors="samanalishiri@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app
ENV CONFIG_DIR=/app/config
ENV OUTPUT_DIR=/app/output

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY config ./config
COPY data ./data
COPY scripts ./scripts

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

CMD ["sh", "-c", "for config in ./config/*.json; do python -m test_data --config \"$config\" || exit 1; done; exec python -m test_data.api.dataset_api"]
