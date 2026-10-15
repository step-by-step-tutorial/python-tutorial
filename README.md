<h1 align="center">Python Tutorial</h1>

Four Python projects that together take generated data from an API, through a data platform, to a machine learning
model.

```text
Python Tutorial
    geodata_pipeline    builds real street addresses per city for test_data
    test_data           generates test datasets and serves them through a REST API
    data_platform       ingests, cleans, validates, enriches and exposes each dataset
    ml_platform         trains and runs a model on the enriched data
```

## Project Structure

```text
python-tutorial
├── geodata_pipeline/                    address source for test_data
├── test_data/                           test data generator and REST API
├── data_platform/                       data platform pipelines and Airflow DAGs
├── ml_platform/                         model training and prediction
├── docker-compose-infrastructure.yml    database, data lake, warehouse and Kafka
└── docker-compose.yml                   the infrastructure plus every project, Airflow, Spark and MLflow
```

Each project has its own README with the details. All commands below run from the repository root.

## 1. Prerequisite

* Python 3.12+
* Java, for the Spark pipeline
* Docker

```shell
python --version
pip --version
java --version
docker --version
```

## 2. Install

```shell
python -m pip install --upgrade pip
pip install -r ./geodata_pipeline/requirements.txt
pip install -e ./geodata_pipeline
pip install -r ./test_data/requirements.txt
pip install -e ./test_data
pip install -r ./data_platform/requirements.txt
pip install -e ./data_platform
pip install -r ./ml_platform/requirements.txt
pip install -e ./ml_platform
```

## 3. Test

```shell
pytest ./geodata_pipeline
pytest ./test_data
pytest ./data_platform
pytest ./ml_platform
```

## 4. Start the Infrastructure

```shell
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test up --build -d
```

## 5. Run

Generate the datasets and serve them through the API:

```shell
python -m test_data
PORT=8084 python -m test_data.api.dataset_api
```

In a second terminal, run a data platform pipeline, then train and run the model on its output:

```shell
DATA_SIMULATOR_API_URL=http://localhost:8084 python -m data_platform.main house inmemory
ML_PLATFORM_DATASET_SOURCE=download python -m ml_platform.main house train
ML_PLATFORM_DATASET_SOURCE=download python -m ml_platform.main house predict
```

## 6. Stop the Infrastructure

```shell
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
```

## 7. Run with Docker

```shell
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev up --build -d
```

```shell
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev down -v
docker rmi samanalishiri/test-data:latest
docker rmi samanalishiri/data-platform:latest
docker rmi samanalishiri/ml-platform:latest
```

## 8. Services

* Airflow: [http://localhost:8082](http://localhost:8082)
    * Username: admin
    * Password: admin
* Test Data API: [http://localhost:8084](http://localhost:8084)
    * API documentation: [http://localhost:8084/docs](http://localhost:8084/docs)
* MLflow: [http://localhost:5000](http://localhost:5000)
* Spark Master: [http://localhost:8080](http://localhost:8080)
* Spark Worker: [http://localhost:8081](http://localhost:8081)
* Data Lake: [http://localhost:9001](http://localhost:9001)
    * Username: admin
    * Password: administrator
* Data Warehouse HTTP: [http://localhost:8123](http://localhost:8123)
    * Username: admin
    * Password: admin
* Database: [http://localhost:8083](http://localhost:8083)
    * Server: database:5432
    * Username: admin
    * Password: admin
    * Database: app_database
    * =======================
    * Server: airflow-database:5432
    * Username: admin
    * Password: admin
    * Database: sale_airflow
* Kafka: [http://localhost:9002](http://localhost:9002)

## 9. Clean

```shell
rm -rf ./geodata_pipeline/output ./geodata_pipeline/src/*.egg-info
rm -rf ./test_data/output ./test_data/output_test ./test_data/src/*.egg-info
rm -rf ./data_platform/report ./data_platform/.coverage ./data_platform/src/*.egg-info
rm -rf ./ml_platform/models/* ./ml_platform/audit_log/* ./ml_platform/output/* ./ml_platform/mlruns/*
rm -rf ./ml_platform/src/*.egg-info
```
