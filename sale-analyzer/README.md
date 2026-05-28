# Sale Analyzer

```shell
python -m pip install --upgrade pip
```

```shell
pip install -r requirements.txt
```

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

```shell
python -m src.main
```

```shell
docker compose --file docker-compose.yml --project-name dev up --build -d
```