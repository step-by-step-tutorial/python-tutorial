FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    build-essential \
    curl \
    && apt-get clean

RUN pip install --no-cache-dir notebook jupyterlab pyspark pandas

ENV PORT=8888
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

EXPOSE $PORT

CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=$PORT --no-browser --allow-root --NotebookApp.token=''"]