# Python Tutorial

## Prerequisite

* Python
* Java
* Docker

## Prepare Environment

```shell
python --version
pip --version
java --version
python -m pip install --upgrade pip
pip install -r ./data_platform/requirements.txt
pip install -e ./data_platform
pip install -r ./test_data/requirements.txt
pip install -e ./test_data
```

```shell
docker --version
```

## Test

```shell
pytest ./data_platform
pytest ./ml_prediction
pytest ./test_data
```

```shell
pytest ./data_platform --html=./data_platform/report/test/test-report.html
pytest ./data_platform --cov --cov-report=html:./data_platform/report/coverage
python -m http.server 8000 --directory ./data_platform/report
```

## LocalHost

```shell
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test up --build -d
```

```shell
python -m test_data --config ./test_data/config/online_shopping.json
python -m test_data --config ./test_data/config/house.json
python -m test_data --config ./test_data/config/house_los_angeles.json
```

```shell
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\test_data
python -m test_data.api.dataset_api
```

```shell
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\data_platform
python -m data_platform.main
```

```shell
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\ml_prediction
python -m ml_prediction.main
```


```shell
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
```

## Dockerization

```shell
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev up --build -d
```

```shell
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev down -v
docker rmi samanalishiri/data-platform:latest
docker rmi samanalishiri/test-data:latest
docker rmi samanalishiri/ml_prediction:latest
```

## Services

* Airflow: [http://localhost:8082](http://localhost:8082)
    * user: admin
    * password: admin
* Test Data API: [http://localhost:8084](http://localhost:8084)
    * API documentation: [http://localhost:8084/docs](http://localhost:8084/docs)
* Spark Master: http://localhost:8080
* Spark Worker: http://localhost:8081
* Datalake: http://localhost:9001
    * Username: admin
    * Password: administrator
* Datawarehouse HTTP: http://localhost:8123
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
    * Database: sale_airflow
* Kafka: http://localhost:9002/

## Clean Directory

```shell
rm ./data_platform/output/*
rm -rf ./data_platform/report
rm -rf ./data_platform/src/*.egg-info
rm -rf ./data_platform/.coverage
rm -rf ./ml_prediction/src/*.egg-info
rm -rf ./ml_prediction/models/*
rm -rf ./ml_prediction/reports/*
rm -rf ./test_data/src/*.egg-info
rm -rf ./test_data/output_test/*
```
