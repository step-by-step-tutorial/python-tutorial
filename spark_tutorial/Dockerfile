FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y openjdk-17-jdk && apt-get clean

RUN pip install --no-cache-dir notebook jupyterlab pyspark panda

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
