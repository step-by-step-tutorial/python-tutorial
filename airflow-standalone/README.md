# <p align="center">Python and Standalone Airflow Tutorial</p>

Apache Airflow is an open-source platform for developing, scheduling, and monitoring batch-oriented workflows. for more
information refer to [https://airflow.apache.org](https://airflow.apache.org).

## Examples

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
    image: apache/airflow:slim-2.9.3-python3.12
    container_name: airflow-standalone
    hostname: airflow-standalone
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
      AIRFLOW__SMTP__SMTP_HOST: mailhog
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
  mailhog:
    image: mailhog/mailhog
    container_name: mailhog
    ports:
      - "1025:1025" # SMTP port
      - "8025:8025" # Web UI port

```

### Apply docker Compose

```shell
docker compose --file ./docker-compose.yml --project-name airflow-standalone up -d --build

```

### Setup Airflow

Connect to Apache Airflow container.

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

#### Add AWS Connection

```shell
airflow connections add localstack_conn \
    --conn-type aws \
    --conn-host http://localstack \
    --conn-port 4566 \
    --conn-login test \
    --conn-password test \
    --conn-extra '{"region_name": "us-west-2", "aws_access_key_id": "test", "aws_secret_access_key": "test", "endpoint_url": "http://localstack:4566"}'
```

```shell
pip install pytest
pip install apache-airflow-providers-amazon

```

### Wen Console

[http://localhost:8080](http://localhost:8080)

```yaml
Username: airflow
Password: airflow
```

### Localstack Command Example

```shell
docker exec -it localstack awslocal s3api create-bucket --bucket test-bucket
```

```shell
docker exec -it localstack awslocal s3 ls
```

```yaml
URL: http://s3.localhost.localstack.cloud:4566
```

### SMTP Server

```shell
docker exec -it mailhog sh
echo -e "Subject: Test Email\n\nThis is a test email sent via sendmail using MailHog." | sendmail -S mailhog:1025 -v test@host.local
```

## Test

```shell
docker exec airflow-standalone pytest /opt/airflow/dags/
```

##

**<p align="center"> [Top](#python-and-standalone-airflow-tutorial) </p>**
