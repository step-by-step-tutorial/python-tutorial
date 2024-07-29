# <p align="center">Python and Standalone Airflow Tutorial</p>

Apache Airflow is an open-source platform for developing, scheduling, and monitoring batch-oriented workflows. for more
information refer to [https://airflow.apache.org](https://airflow.apache.org).

## Prerequisites

* [Python 3](https://www.python.org)
* [Apache Airflow](https://airflow.apache.org)
* [Docker](https://www.docker.com)

## Update PIP

```shell
python.exe -m pip install --upgrade pip
```

## Install Packages

```shell
pip install -r requirements.txt
```

## Install Apache Airflow on Docker

### Docker Compose

[docker-compose.yml](docker-compose.yml)

```yaml
version: '3.8'
services:
  airflow-standalone:
    image: apache/airflow:2.9.1
    container_name: airflow-standalone
    hostname: airflow-standalone
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: >
      bash -c "
      airflow db init &&
      airflow users create -u admin -p admin -f Admin -l User -r Admin -e admin@example.com &&
      airflow webserver --port 8080 & 
      airflow scheduler
      "
```

### Apply docker Compose

```shell
docker compose --file ./docker-compose.yml --project-name airflow-standalone up -d --build

```

### Setup Airflow

Connect to apache Airflow container.

```shell
docker exec -it airflow-standalone bash
```

#### Create User.

```shell
airflow users create \
    --username airflow \
    --firstname Name \
    --lastname Surname \
    --role Admin \
    --email airflow@example.com \
    --password airflow
```

### Wen Console

[http://localhost:8080](http://localhost:8080)

## Test

```shell
docker exec airflow-standalone pytest /opt/airflow/dags/test_hello_world.py
```

##

**<p align="center"> [Top](#python-and-standalone-airflow-tutorial) </p>**
