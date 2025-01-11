# <p align="center">Python and Spark Tutorial</p>

This tutorial provides examples regarding Spark and Python.

## <p align="center">Table of Content</p>

* [Spark Introduction](#spark-introduction)
    * [Key Features](#key-features)
    * [Use Cases](#use-cases)
* [Core Concepts](#core-concepts)
    * [Resilient Distributed Datasets (RDDs)](#resilient-distributed-datasets-rdds)
    * [Partitioning](#partitioning)
    * [Directed Acyclic Graph (DAG)](#directed-acyclic-graph-dag)
    * [Lazy Evaluation](#lazy-evaluation)
    * [Immutability](#immutability)
    * [In-Memory Computing](#in-memory-computing)
    * [Fault Tolerance](#fault-tolerance)
    * [Spark's Ecosystem and APIs](#sparks-ecosystem-and-apis)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
    * [Install Python](#install-python)
    * [Install Spark On Docker](#install-spark-on-docker)
    * [Test](#test)
* [Steps](#steps)

## Spark Introduction

Apache Spark is a multi-language and open-source engine designed for large-scale data processing and analytics. It
supports high-performance tasks in data engineering, data science, machine learning and providing capabilities for both
batch and real-time data processing.

### Key Features

* Batch/streaming data
* SQL analytics
* Data science at scale
* Machine learning

### Use Cases

* Real-Time Data Processing
* Machine Learning
* Graph Processing
* Data Warehousing

## Core Concepts

* Resilient Distributed Datasets (RDDs)
* Partitioning
* Directed Acyclic Graph (DAG)
* Lazy Evaluation
* Immutability
* In-Memory Computing
* Fault Tolerance
* Spark's Ecosystem and APIs

### Resilient Distributed Datasets (RDDs)

RDDs are the fundamental building blocks of Apache Spark. They consist of collections of elements partitioned across the
nodes of a cluster that can be operated on in parallel. This structure allows developers to perform read-only data
transformations such as map, filter, and join operations in a distributed and fault-tolerant manner.

### Partitioning

It refers to the division of data across different nodes in a Spark cluster to facilitate parallel processing. Effective
partitioning optimizes the distribution of data and the computational load across the cluster, enhancing performance and
scalability.

### Directed Acyclic Graph (DAG)

Spark builds a DAG to outline workflows and execute data transformations. Each node in the DAG represents an RDD, and
the edges represent transformations that produce new RDDs. This mechanism allows for optimized execution plans by
minimizing unnecessary data transfers and enabling complex computation pipelines.

### Lazy Evaluation

Spark employs lazy evaluation to optimize the execution of data processing tasks. Computations on RDDs are only executed
when an action that requires an output is performed. This approach reduces computational overhead by executing multiple
operations in a single pass over the data, thus improving performance.

### Immutability

Once created, RDDs cannot be changed. Every transformation on an RDD results in a new RDD, ensuring data consistency and
fault tolerance. Immutability facilitates easy recovery from node failures and prevents data corruption by ensuring that
errors do not propagate through subsequent operations.

### In-Memory Computing

Spark's design emphasizes in-memory data processing, allowing it to perform operations much faster than disk-based
systems. Therefore, by reducing the need for disk I/O, Spark accelerates data processing and offers significant
performance improvements over traditional disk-based systems.

### Fault Tolerance

Spark achieves fault tolerance using the lineage of RDDs, which allows it to recover lost data due to node failures. If
a part of the data processing pipeline fails, Spark can recompute the lost parts without needing to start over from
scratch. Ensures continuous operation and data integrity across large clusters, making Spark reliable for critical
applications.

### Spark's Ecosystem and APIs

The ecosystem extends Spark's capabilities through Spark SQL, MLlib, GraphX, and Spark Streaming, among others. Spark
supports multiple programming languages, enabling developers to build complex applications using their preferred tools.
A broad ecosystem and versatile APIs make Spark adaptable for a variety of use cases, from batch processing to real-time
data streaming and machine learning.

## Prerequisites

* [Python 3](https://www.python.org)
* [Spark](https://spark.apache.org)
* [Docker](https://www.docker.com)

## Setup

### Install Python

#### Windows
Download Python installer from [https://www.python.org](https://www.python.org) then run installer.

#### Linux/Unix
For Linux/Unix just execute the following command.

```shell
# ubuntu
sudo apt-get install python3
```

```shell
# fedora
sudo dnf install python3
```

#### Test

```shell
python --version
```

#### Dependencies

```shell
python -m pip install --upgrade pip
pip install pyspark
pip install pytest
pip install pytest-html
pip install pytest-cov
```

Install from Requirements.txt

```shell
pip install -r requirements.txt
```

### Install Spark On Docker

#### Docker Compose
Creat Dockerfile for install Jupyter Notebook.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y openjdk-17-jdk && apt-get clean
RUN pip install --no-cache-dir notebook jupyterlab pyspark pandas

ENV PORT=8888

EXPOSE $PORT

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=$PORT", "--no-browser", "--allow-root"]
```

Create a file named docker-compose.yml then add the following content to the file.

```yaml
version: "3.9"

services:
  master:
    image: docker.io/bitnami/spark:latest
    container_name: master
    hostname: master
    user: root
    environment:
      SPARK_MODE: master
      SPARK_RPC_AUTHENTICATION_ENABLED: no
      SPARK_RPC_ENCRYPTION_ENABLED: no
      SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED: no
      SPARK_SSL_ENABLED: no
    ports:
      - "8080:8080"
      - "7077:7077"
    volumes:
      - "./resources:/resources"
  worker:
    image: docker.io/bitnami/spark:latest
    container_name: worker
    hostname: worker
    user: root
    environment:
      SPARK_MODE: worker
      SPARK_MASTER_URL: spark://master:7077
      SPARK_RPC_AUTHENTICATION_ENABLED: no
      SPARK_RPC_ENCRYPTION_ENABLED: no
      SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED: no
      SPARK_SSL_ENABLED: no
    ports:
      - "8081:8081"
    volumes:
      - "./resources:/resources"
  jupyter:
    image: samanalishiri/notebook:latest
    build:
      context: .
      dockerfile: Dockerfile
    container_name: jupyter
    hostname: jupyter
    user: root
    ports:
      - "8888:8888"
    volumes:
      - "./resources:/resources"
    environment:
      PORT: 8888
```

#### Apply Docker Compose

Execute the following command to create and start Spark container.

```shell
docker compose --project-name spark_tutorial up -d --build
```

#### Test Containerized Tools

```shell
docker exec master spark-submit --version
```

```shell
docker exec master java --version
```

```shell
docker exec master python --version
```

```shell
docker exec jupyter java --version
```

```shell
docker exec jupyter python --version
```

#### Web Console

Master Spark UI: [http://localhost:8080](http://localhost:8080)
Worker Spark UI: [http://localhost:8081](http://localhost:8081)
Jupyter UI: [http://localhost:8888](http://localhost:8888)

#### Jupyter

After login into Jupyter then upload [ipynb](./spark-lab.ipynb)

```python
#%%
from pyspark.sql import SparkSession

APP_NAME = "Tutorial: Jupyter Application"
MASTER_URL = "spark://master:7077"
DRIVER_HOST = "jupyter"
DRIVER_BIND_ADDRESS = "0.0.0.0"

session = SparkSession.builder \
    .appName(APP_NAME) \
    .master(MASTER_URL) \
    .config("spark.driver.host", DRIVER_HOST) \
    .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
    .getOrCreate()
print("Spark session established.")

columns = ["row", "number"]
data = [("row1", 1), ("row2", 2), ("row3", 3)]
data_frame = session.createDataFrame(data, schema=columns)
data_frame.show()

session.stop()
print("Spark session closed.")
#%%

from IPython.display import display


def print_table(data_frame, title="Styled Data Table"):
    df = data_frame.toPandas()

    styled_table = (
        df.style.set_table_styles(
            [
                {"selector": "thead th",
                 "props": [("background-color", "#4CAF50"), ("color", "black"), ("text-align", "center"),
                           ("padding", "10px")]},
                {"selector": "tbody td",
                 "props": [("border", "1px solid #ddd"), ("text-align", "center"), ("padding", "5px")]},
                {"selector": "caption",
                 "props": [("caption-side", "top"), ("font-size", "24px"), ("font-weight", "bold"),
                           ("text-align", "left")]},
            ]
        )
        .set_caption(title)
        .apply(
            lambda x: ["background-color: white" if i % 2 == 0 else "background-color: #d4f7dc" for i in range(len(x))],
        )
        .hide(axis="index")
    )

    display(styled_table)

#%%
from pyspark.sql import SparkSession

APP_NAME = "Tutorial: DataFrame Basic Operation"
MASTER_URL = "spark://master:7077"
DRIVER_HOST = "jupyter"
DRIVER_BIND_ADDRESS = "0.0.0.0"

session = SparkSession.builder \
    .appName(APP_NAME) \
    .master(MASTER_URL) \
    .config("spark.driver.host", DRIVER_HOST) \
    .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
    .getOrCreate()
session.sparkContext.setLogLevel("WARN")
print("Spark session established.")

csv_path = "/resources/persons.csv"
print(f"Reading CSV file from: {csv_path}")
data_frame = session.read.options(header=True, inferSchema=True).csv(csv_path)
data_frame.createOrReplaceTempView("persons")

print_table(data_frame.limit(10), "Persons")

session.stop()
print("Spark session closed.")
#%%
```

## Pipeline

### Test

```shell
pytest
```

```shell
pytest --html=./report/test/test-report.html
```

```shell
pytest --cov --cov-report=html:report/coverage
```

```shell
python -m http.server 8000 --directory ./report
```

## Steps

* [step: Establish Connection](establish_connection)
* [step: CSV Manipulation](csv_manipulation)
* [step: DataFrame Basic Operation](data_frame_basic)

##

**<p align="center"> [Top](#python-and-spark-tutorial) </p>**
