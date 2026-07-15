# Sale Data Platform

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
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\sale_data_platform
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
docker rmi samanalishiri/application:latest
```

## UI
Datalake: [http://localhost:9001](http://localhost:9001)
* user: admin
* password: administrator

Datawarehouse: [http://localhost:8123](http://localhost:8123)
* user: admin
* password: admin

Database: [http://localhost:8080](http://localhost:8080)
* Username: admin
* Password: admin
* Server: database:5432
* Database: sale_oltp


## Clean Directory

```shell
rm ./output/*
rm -rf ./report
rm -rf ./src/sale_data_platform.egg-info
rm ./.coverage
```

