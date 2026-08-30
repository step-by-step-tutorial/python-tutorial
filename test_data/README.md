# Test Data Generator

## Prerequisites

* Python
* Docker

## Prepare Environment

```shell
python --version
pip --version
python -m pip install --upgrade pip
pip install -r ./test_data/requirements.txt
pip install -e ./test_data
```

## Test

```shell
cd ./test_data
pytest
```

## Local

```shell
cd ./test_data
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file ./.env.test up --build -d
```

```shell
cd ./test_data
python -m test_data --config ./config/online_shopping.json
python -m test_data --config ./config/house.json
python -m test_data --config ./config/house_los_angeles.json
python -m test_data --help
```

```shell
cd ./test_data
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\test_data
python -m test_data.api.dataset_api
```

URL: [localhost:8084](http://localhost:8084)
API Documentation: [localhost:8084/docs](http://localhost:8084/docs)
ReDoc: [localhost:8084/redoc](http://localhost:8084/redoc)

```shell
cd ./test_data
docker compose --file docker-compose-infrastructure.yml --project-name test --env-file ./.env.test down -v
```

## Dockerize

```shell
cd ./test_data
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev up --build -d
```

```shell
cd ./test_data
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev down -v
docker rmi samanalishiri/test-data:latest
```

## Clean

```shell
rm -rf ./test_data/src/*.egg-info
rm -rf ./test_data/output_test/*
```