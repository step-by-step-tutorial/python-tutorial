
FROM spark:4.1.2-python3

USER root
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY tests ./tests
COPY data ./data

ENV PYTHONPATH=/app

CMD ["python3", "-m", "src.main"]
