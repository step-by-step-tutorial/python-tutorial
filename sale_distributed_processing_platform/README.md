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
docker compose --file docker-compose-infrastructure.yml --project-name dev up --build -d
```

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

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose-infrastructure.yml --project-name dev down -v
```

## LocalHost

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose-infrastructure.yml --project-name dev up --build -d
```


```shell
cd ./sale_distributed_processing_platform
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\sale_etl_orchestration-platform
python ./src/main.py
```

```shell
cd ./sale_distributed_processing_platform
docker compose --file docker-compose-infrastructure.yml --project-name dev down -v
```

## Dockerization

```shell
docker compose --file docker-compose.yml --project-name dev up --build -d
```

```shell
docker compose --file docker-compose.yml --project-name dev down -v
```

## Services

* Spark Master: http://localhost:8081
* Spark Worker: http://localhost:8082
* MinIO: http://localhost:9001
* ClickHouse HTTP: http://localhost:8123
* PostgreSQL: http://localhost:5432

## Clean Directory

```shell
rm ./output/*
rm -rf ./report
rm -rf ./src/sale-distributed-processing-platform.egg-info
rm ./.coverage
```
