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
python -m src.main
```

## Dockerization

```shell
docker compose --file docker-compose.yml --project-name dev up --build -d
```

```shell
docker compose --file docker-compose.yml --project-name dev down -v
```