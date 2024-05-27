# <p align="center">Python and Spark Tutorial</p>

This tutorial provides examples regarding Spark and Python.

# <p align="center">Table of Content</p>

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
* [Steps](#steps)
* [Pipeline](#pipeline)

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

Download Python installer from [https://www.python.org](https://www.python.org) then run installer and for Linux/Unix
just execute the following command.

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
pip install pyspark
pip install pytest
pip install pytest-html
pip install pytest-cov
```

Install from Requirements.txt

```shell
pip install -r requirements.txt
pip list
```

### Install Spark On Docker

Create a file named docker-compose.yml then add the following content to the file.

```yaml
version: "3.8"

services:
  spark:
    image: docker.io/bitnami/spark:latest
    container_name: spark
    hostname: spark
    user: root
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    ports:
      - "8080:8080"
      - "7077:7077"
  spark-worker:
    image: docker.io/bitnami/spark:latest
    container_name: spark-worker
    hostname: spark-worker
    user: root
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark:7077
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    ports:
      - "8081:8081"
  jupyter:
    image: jupyter/base-notebook:latest
    container_name: jupyter
    hostname: jupyter
    user: root
    ports:
      - "8888:8888"
    volumes:
      - ./data:/home/jovyan/work
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - NB_UID=1000
      - NB_GID=100
      - GRANT_SUDO=yes
```

Execute the following command to create and start Spark container.

```shell
docker compose --project-name spark up -d --build
```

#### Test

SparkUI: [http://localhost:8080](http://localhost:8080)

JupyterUI: [http://localhost:8888](http://localhost:8888)

#### Jupyter

Open Jupyter via web browser and create a console then execute the following commands.

```shell
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install openjdk-17-jdk
java -version

```

In order to check connectivity between Jupyter and Spark create ipynb then use the code fragment in the below.

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("Jupyter Application")
         .master("spark://master:7077")
         .getOrCreate())

columns = ["text", "number"]
data = [("row1", 1), ("row2", 2), ("row3", 3)]

data_frame = spark.createDataFrame(data, schema=columns)

data_frame.show()

spark.stop()
```

```textmate
# output
+----+------+
|text|number|
+----+------+
|row1|     1|
|row2|     2|
|row3|     3|
+----+------+
```

## Steps

* [step: Establish Connection](establish_connection)
* [step: CSV Manipulation](csv_manipulation)
* [step: DataFrame Basic Operation](data_frame_basic_operation)

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

##

**<p align="center"> [Top](#python-and-spark-tutorial) </p>**
