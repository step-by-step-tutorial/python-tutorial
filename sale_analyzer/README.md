# Sale Analyzer

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
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\sale_analyzer
python ./src/main.py
```

## Dockerization

```shell
docker compose --file docker-compose.yml --project-name dev up --build -d
```

```shell
docker compose --file docker-compose.yml --project-name dev down -v
docker rmi samanalishiri/application:latest
```

## Clean Directory

```shell
rm ./output/*
rm -rf ./report
rm -rf ./src/sale_analyzer.egg-info
rm ./.coverage
```

