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
python ./test_data/src/test_data/main.py --config ./config/sale.json
python ./test_data/src/test_data/main.py --config ./config/online_shopping.json
python ./test_data/src/test_data/main.py --config ./config/hr.json
```

```shell
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\test_data
python ./test_data/src/test_data/api/dataset_api.py 
```

```shell
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\data_platform
python ./data_platform/src/main.py
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
docker rmi samanalishiri/application:latest
```

## Services

* Airflow: [http://localhost:8082](http://localhost:8082)
    * user: admin
    * password: admin
* Spark Master: http://localhost:8080
* Spark Worker: http://localhost:8181
* Datalake: http://localhost:9001
    * Username: admin
    * Password: administrator
* Datawarehouse HTTP: http://localhost:8123
    * Username: admin
    * Password: admin
* Database: http://localhost:8500
    * Server: database:5432
    * Username: admin
    * Password: admin
    * Database: app_database
    * =======================
    * Server: airflow-database:5432
    * Username: admin
    * Password: admin
    * Database: sale_airflow

## Clean Directory

```shell
rm ./data_platform/output/*
rm -rf ./data_platform/report
rm -rf ./data_platform/src/data_platform.egg-info
rm ./data_platform/.coverage
rm ./test_data/output/*
rm -rf ./test_data/report
rm -rf ./test_data/src/test_data.egg-info
rm ./test_data/.coverage
```
