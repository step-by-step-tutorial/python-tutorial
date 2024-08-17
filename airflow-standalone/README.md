# <p align="center">Integration of Python and Standalone Airflow</p>

Apache Airflow is an open-source platform for developing, scheduling, and monitoring batch-oriented workflows. for more
information refer to [https://airflow.apache.org](https://airflow.apache.org).

## Core Concepts

### DAG (Directed Acyclic Graph)

A collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies. In
Airflow, a DAG describes how to run a workflow.

### Task

A defined unit of work within a DAG. Each task is represented as an operator in Airflow.

### Operator

A template for a task. Airflow provides various operators, such as:
BashOperator: Executes a Bash script.
PythonOperator: Executes a Python callable.
SqlOperator: Executes an SQL command.
Sensor: Waits for a certain condition to be met (e.g., a file appearing on a filesystem).

### Task Instance

A specific run of a task, with a defined execution date. Task instances are the representation of a task at a certain
point in time.

### Executor

Determines how and where tasks get executed. Common executors include the SequentialExecutor (for local runs) and the
CeleryExecutor (for distributed tasks).

### Scheduler

Responsible for triggering the tasks in a DAG based on the defined schedule. The scheduler scans and triggers tasks as
their dependencies are met.

### Worker

A worker is a process that actually executes the task. Workers can be on the same machine as the scheduler or
distributed across many machines.

### Hooks

Interfaces to external platforms or services. Hooks abstract the interaction with external systems like databases, cloud
services, and more.

### Connections

Configured credentials and parameters used by hooks to connect to external systems (e.g., database credentials, API
keys).

### XCom (Cross-Communication)

Mechanism that allows tasks to exchange messages or small amounts of data.

### Trigger Rules

Define how tasks should be triggered based on the state of their upstream tasks (e.g., trigger if all upstream tasks
succeed).

### Branching

Allows for the creation of conditional paths within a DAG, where certain tasks are run only under specific conditions.

### Pools

Limits the parallelism of certain tasks by creating a pool of slots that can be shared across tasks.

### Variable

Key-value pairs that are made available for use in DAGs and tasks.

### Plugins

Allow users to extend the functionality of Airflow, such as adding custom operators, hooks, and executors.

### SubDAG

A DAG within a DAG, useful for complex workflows that need to be logically separated into smaller units.

### DAG Runs

Instances of a DAG in a specific execution period, representing a single execution of the DAG.

### Task Lifecycle

The states a task can be in during its execution: queued, running, success, failure, skipped, etc.

## Getting Started

### Prerequisites

* [Python 3](https://www.python.org)
* [Apache Airflow](https://airflow.apache.org)
* [Docker](https://www.docker.com)

### Install Python Packages

```shell
python.exe -m pip install --upgrade pip
```

```shell
pip install -r requirements.txt
```

### Install Apache Airflow on Docker

#### Docker Compose

[docker-compose.yml](docker-compose.yml)

```yaml
version: '3.8'
services:
  airflow-standalone:
    image: apache/airflow:slim-2.9.3-python3.12
    container_name: airflow-standalone
    hostname: airflow-standalone
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
      AIRFLOW__SMTP__SMTP_HOST: smtp-server
      AIRFLOW__SMTP__SMTP_STARTTLS: False
      AIRFLOW__SMTP__SMTP_SSL: False
      AIRFLOW__SMTP__SMTP_USER: ""
      AIRFLOW__SMTP__SMTP_PASSWORD: ""
      AIRFLOW__SMTP__SMTP_PORT: 1025
      AIRFLOW__SMTP__SMTP_MAIL_FROM: airflow@example.com
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
      - ./resources:/opt/airflow/resources
    ports:
      - "8080:8080"
    command: >
      bash -c "
      airflow db init &&
      airflow users create -u admin -p admin -f Admin -l User -r Admin -e admin@example.com &&
      airflow webserver --port 8080 & 
      airflow scheduler
      "
  localstack:
    container_name: localstack
    hostname: localstack
    image: localstack/localstack
    ports:
      - "4566:4566"
      - "4510-4559:4510-4559"
  smtp-server:
    image: mailhog/mailhog
    container_name: smtp-server
    hostname: smtp-server
    ports:
      - "1025:1025"
      - "8025:8025"
```

#### Apply docker Compose

```shell
docker compose --file ./docker-compose.yml --project-name airflow-standalone up -d --build

```

#### Setup Airflow

Connect to Apache Airflow container.

```shell
docker exec -it airflow-standalone bash
```

##### Install Python Packages

```shell
pip install pytest
pip install apache-airflow-providers-amazon

```

##### Create User.

```shell
airflow users create \
    --username airflow \
    --firstname Name \
    --lastname Surname \
    --role Admin \
    --email airflow@example.com \
    --password airflow
```

##### Add AWS Connection

```shell
airflow connections add localstack_conn \
    --conn-type aws \
    --conn-host http://localstack \
    --conn-port 4566 \
    --conn-login test \
    --conn-password test \
    --conn-extra '{"region_name": "us-west-2", "aws_access_key_id": "test", "aws_secret_access_key": "test", "endpoint_url": "http://localstack:4566"}'
```

#### Wen Console

[http://localhost:8080](http://localhost:8080)

```yaml
Username: airflow
Password: airflow
```

#### Localstack S3

##### Create Bucket

```shell
docker exec -it localstack awslocal s3api create-bucket --bucket test-bucket
```

##### List of Bucket

```shell
docker exec -it localstack awslocal s3 ls
```

##### List of Bucket Via Browser

```yaml
URL: http://s3.localhost.localstack.cloud:4566
```

#### SMTP Server

In order to test SMTP server (mailhog) connect to SMTP server container then send a test email.

```shell
docker exec -it smtp-server sh
```

```shell
echo -e "Subject: Test Email\n\nThis is a test email sent via sendmail using smtp-server." | sendmail -S smtp-server:1025 -v test@host.local
```

```yaml
URL: http://localhost:8025
```

### Test

```shell
docker exec airflow-standalone pytest /opt/airflow/dags/
```

## Steps

* [Basic DAG Creation](/airflow-standalone/dags/hello_world.py)
* [Task Dependencies (Bash)](/airflow-standalone/dags/bash_dependency.py)
* [Task Dependencies (Python)](/airflow-standalone/dags/python_dependency.py)
* [Branching in DAGs](/airflow-standalone/dags/branching.py)
* [Triggering External Tasks (Parent)](/airflow-standalone/dags/parent.py)
* [Triggering External Tasks (Child)](/airflow-standalone/dags/child.py)
* [XCom for Task Communication](/airflow-standalone/dags/xcom.py)
* [Task Retry and Timeout](/airflow-standalone/dags/retry_timeout.py)
* [Parallel Task Execution](/airflow-standalone/dags/parallel_tasks.py)
* [Integrating with AWS](/airflow-standalone/dags/s3_integration.py)
* [Monitoring and Alerts](/airflow-standalone/dags/monitoring_alerting.py)
* [Using Macros and Jinja Templates](/airflow-standalone/dags/)

##

**<p align="center"> [Top](#integration-of-python-and-standalone-airflow) </p>**
