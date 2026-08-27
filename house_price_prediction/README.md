# House Price Prediction

## Machine Learning Layer

```text
Machine Learning Layer
    dataset preparation
    feature engineering
    train/validation/test split
    baseline model
    model training
    evaluation
    model persistence
    prediction
    monitoring
```

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
pip install -r ./requirements.txt
pip install -e .
```

```shell
docker --version
```

## Test

```shell
cd ./house_price_prediction
pytest
```

```shell
cd ./house_price_prediction
pytest --html=./report/test/test-report.html
pytest --cov --cov-report=html:./report/coverage
python -m http.server 8000 --directory ./report
```

## LocalHost


```shell
cd ./house_price_prediction
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\house_price_prediction
python -m house_price_prediction.main house
```

