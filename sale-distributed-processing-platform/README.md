
# Sale Data Platform

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
pip install -r requirements.txt
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
python -m src.main
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

## Services

* Airflow: http://localhost:8080
* Spark Master: http://localhost:8081
* Spark Worker: http://localhost:8082
* MinIO: http://localhost:9001
* ClickHouse HTTP: http://localhost:8123
