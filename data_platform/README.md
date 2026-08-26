# Data Platform

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
pip install -r ./requirements.txt
pip install -e .
```

```shell
docker --version
```

## Test

```shell
cd ./data_platform
pytest
```

```shell
cd ./data_platform
pytest --html=./report/test/test-report.html
pytest --cov --cov-report=html:./report/coverage
python -m http.server 8000 --directory ./report
```

## LocalHost

```shell
cd ./data_platform
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test up --build -d
```

```shell
cd ./data_platform
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\data_platform
python -m data_platform.main house
```


```shell
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
```

## Dockerization

```shell
cd ./data_platform
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev up --build -d
```

```shell
cd ./data_platform
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev down -v
docker rmi samanalishiri/data-platform:latest
```

## Services

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

## Clean Directory

```shell
rm ./output/*
rm -rf ./report
rm -rf ./src/data_platform.egg-info
rm -rf ./.coverage
```
