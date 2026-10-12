<h1 align="center">Data Platform</h1>

Runs each registered dataset (`house`, `online_shopping`) through the same pipeline, either in memory with pandas or
with Spark. Every step is written to the data lake, and the result is exposed to the database and the warehouse.

```text
Data Platform Pipeline
    prepare
    ingest
    clean
    validate
    enrich
    expose
    analyze
    cleanup
```

## Project Structure

```text
data_platform
├── dags/                     Airflow DAGs, one per dataset and pipeline type
├── resources/                sample CSV files
├── scripts/                  SQL scripts for the database and the warehouse
├── src/data_platform
│   ├── main.py               command line entry point
│   ├── config/               keys, pipeline type, storage environment, settings
│   ├── model/                all dataclasses: settings, endpoints, dataset, flow, audit events, reports
│   ├── domain/               one package per dataset: attributes, dataset factory, registration
│   ├── registry/             connection, endpoint and dataset registries and their bootstrap
│   ├── connector/            database, data lake, warehouse, Kafka and Spark clients
│   ├── ingestion/            ingestors (pandas and Spark)
│   ├── cleaner/              cleaners (pandas and Spark)
│   ├── validator/            validators (pandas and Spark)
│   ├── enricher/             enrichers (pandas and Spark)
│   ├── analyzer/             analyzers (pandas and Spark)
│   ├── repository/           data lake, database, warehouse and Kafka repositories
│   ├── pipeline/             shared pipeline, inmemory and Spark pipelines, Airflow adapter
│   ├── audit/                audit services and registration
│   └── util/                 general helpers
└── tests
```

All commands below run from the repository root.

## 1. Prerequisite

* Python 3.12+
* Java (for the Spark pipeline)
* Docker

## 2. Prepare Environment

```shell
python --version
pip --version
java --version
docker --version
```

```shell
cd ./data_platform
python -m pip install --upgrade pip
pip install -r ./requirements.txt
pip install -e .
```

## 3. Test

```shell
cd ./data_platform
pytest
```

Spark tests are skipped when `pyspark` is not installed.

```shell
cd ./data_platform
pytest --html=./report/test/test-report.html
pytest --cov --cov-report=html:./report/coverage
python -m http.server 8000 --directory ./report
```

## 4. Start the Infrastructure

```shell
cd ./data_platform
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test up --build -d
```

## 5. Run a Pipeline

Pass the dataset name and the pipeline type (`inmemory` or `spark`):

```shell
cd ./data_platform
python -m data_platform.main house inmemory
python -m data_platform.main online_shopping spark
```

Without arguments, the command asks for both interactively.

## 6. Stop the Infrastructure

```shell
cd ./data_platform
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
```

## 7. Run with Docker

```shell
cd ./data_platform
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev up --build -d
```

```shell
cd ./data_platform
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev down -v
docker rmi samanalishiri/data-platform:latest
```

## 8. Services

* Airflow: [http://localhost:8082](http://localhost:8082)
    * user: admin
    * password: admin
* Spark Master: http://localhost:8080
* Spark Worker: http://localhost:8081
* Datalake: http://localhost:9001
    * Username: admin
    * Password: administrator
* Warehouse HTTP: http://localhost:8123
    * Username: admin
    * Password: admin
* Database: http://localhost:8083
    * Server: database:5432
    * Username: admin
    * Password: admin
    * Database: app_database
    * =======================
    * Server: airflow-database:5432
    * Username: admin
    * Password: admin
    * Database: airflow

## 9. Clean

```shell
rm -rf ./data_platform/report
rm -rf ./data_platform/src/*.egg-info
rm -rf ./data_platform/.coverage
```
