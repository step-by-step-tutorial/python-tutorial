# Sale Distributed Processing Platform

## Prerequisite

* Python
* Java
* Docker

## Prepare Environment

```shell
cd ./sale_distributed_processing_platform
python --version
pip --version
java --version
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

```shell
docker --version
```

## Test

```shell
cd ./sale_distributed_processing_platform
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

## LocalHost

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test up --build -d
```


```shell
cd ./sale_distributed_processing_platform
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\sale_distributed_processing_platform
python ./src/main.py
```

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file .env.test down -v
```

## Dockerization

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose.yml --project-name dev --env-file .env.dev up --build -d
```

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose.yml --project-name dev --env-file .env.dev down -v
docker rmi samanalishiri/application:latest
```

## Services

* Spark Master: http://localhost:8080
* Spark Worker: http://localhost:8181
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
  * Database: sale_database

## Clean Directory

```shell
rm ./output/*
rm -rf ./report
rm -rf ./src/sale_distributed_processing_platform.egg-info
rm ./.coverage
```
