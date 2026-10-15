FROM python:3.12-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app
ENV DL_PLATFORM_DATA_DIR=/app/data
ENV DL_PLATFORM_MODEL_DIR=/app/models
ENV DL_PLATFORM_AUDIT_DIR=/app/audit_log
ENV DL_PLATFORM_OUTPUT_DIR=/app/output

WORKDIR /app

COPY pyproject.toml ./
COPY requirements.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install -r requirements.txt

COPY src ./src

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install .

ENTRYPOINT ["python", "-m", "dl_platform.main"]
