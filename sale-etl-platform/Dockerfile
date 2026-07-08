FROM python:3.12-slim
LABEL authors="samanalishiri@gmail.com"

WORKDIR /app

COPY requirements.txt .
COPY src ./src
COPY tests ./tests
COPY dags ./dags
COPY pyproject.toml .

RUN pip install -e .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python -m main && tail -f /dev/null"]
