FROM python:3.12-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app
ENV ML_PREDICTION_DATA_DIR=/app/data
ENV ML_PREDICTION_MODEL_DIR=/app/models

WORKDIR /app

COPY pyproject.toml ./
COPY requirements.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY src ./src
COPY data ./data

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install .

CMD ["python", "-m", "ml_prediction.main"]
