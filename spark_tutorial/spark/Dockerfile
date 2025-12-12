FROM apache/spark:4.0.1-java21

USER root

ARG PYTHON_VERSION=3.12.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    build-essential \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    uuid-dev \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" -o /tmp/python.tgz \
  && tar -xzf /tmp/python.tgz -C /tmp \
  && cd "/tmp/Python-${PYTHON_VERSION}" \
  && ./configure --enable-optimizations --with-ensurepip=install \
  && make -j"$(nproc)" \
  && make altinstall \
  && ln -sf /usr/local/bin/python3.12 /usr/local/bin/python \
  && ln -sf /usr/local/bin/pip3.12 /usr/local/bin/pip \
  && python --version \
  && pip --version \
  && rm -rf /tmp/python.tgz "/tmp/Python-${PYTHON_VERSION}"

RUN python -m venv /opt/venv && /opt/venv/bin/pip --version

ENV PATH="/opt/venv/bin:/usr/local/bin:${PATH}" \
    PYSPARK_PYTHON="/usr/local/bin/python" \
    PYSPARK_DRIVER_PYTHON="/usr/local/bin/python"

USER 185
