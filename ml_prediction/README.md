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
pip install -r ./ml_prediction/requirements.txt
pip install -e ./ml_prediction/
```

```shell
docker --version
```

## Test

```shell
cd ./ml_prediction
pytest
```

```shell
cd ./ml_prediction
pytest --html=./report/test/test-report.html
pytest --cov --cov-report=html:./report/coverage
python -m http.server 8000 --directory ./report
```

## LocalHost


```shell
cd ./ml_prediction
python -m ml_prediction.main
```

```shell
cd ./ml_prediction
python -m ml_prediction.main house train
```

```shell
cd ./ml_prediction
python -m ml_prediction.main house predict
```

## Clean Project

```shell
rm -rf ./ml_prediction/.coverage
rm -rf ./ml_prediction/*.egg-info
```