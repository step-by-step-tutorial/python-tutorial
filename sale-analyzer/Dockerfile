FROM python:3.12-slim
LABEL authors="samanalishiri@gmail.com"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY data ./data

CMD ["python", "-m", "app.main"]
