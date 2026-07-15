# Sale ETL Platform

## Prerequisite

* Python
* Docker

## Prepare Environment

```shell
python --version
pip --version
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

```shell
docker --version
```

## Test

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

## LocalHost

```shell
docker compose --file docker-compose-infrastructure.yml --project-name dev up --build -d
```

```shell
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\sale_etl_orchestration-platform
python ./src/main.py
```

```shell
docker compose --file docker-compose-infrastructure.yml --project-name dev down -v
```

## Dockerization

```shell
docker compose --file docker-compose.yml --project-name dev up --build -d
```

```shell
docker compose --file docker-compose.yml --project-name dev down -v
```

## UI

airflow: [http://localhost:8080](http://localhost:8080)
* user: admin
* password: admin

datalake: [http://localhost:9001](http://localhost:9001)
* user: admin
* password: administrator

clickhouse: [http://localhost:8123](http://localhost:8123)
* user: admin
* password: admin

adminer: [http://localhost:8081](http://localhost:8081)
* Server: postgres
* Username: admin
* Password: admin
* Database: sale_oltp

## Clean Directory

```shell
rm ./output/*
rm -rf ./report
rm -rf ./src/sale_etl_orchestration-platform.egg-info
rm ./.coverage
```
