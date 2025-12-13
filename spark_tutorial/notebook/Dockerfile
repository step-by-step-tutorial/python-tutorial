FROM alpine:latest
LABEL maintainer="samanalishiri@gmail.com"

RUN apk update && apk add --no-cache \
    openjdk21-jre-headless \
    python3 \
    py3-pip \
    py3-virtualenv \
    ca-certificates \
    bash \
    && ln -sf python3 /usr/bin/python

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apk add --no-cache --virtual .build-deps gcc g++ musl-dev linux-headers python3-dev

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir notebook jupyterlab pyspark pandas

RUN apk del .build-deps

EXPOSE 8888

CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''"]
