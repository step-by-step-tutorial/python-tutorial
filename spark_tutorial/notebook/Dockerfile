FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    build-essential \
    curl \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir notebook jupyterlab pyspark pandas

ENV PORT=8888
EXPOSE $PORT

CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=$PORT --no-browser --allow-root --NotebookApp.token=''"]
