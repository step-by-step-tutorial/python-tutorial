# House Price Prediction

## Machine Learning Layer

```text
Machine Learning Layer
    dataset preparation
    feature engineering
    train/validation/test split
    model training
    evaluation
    model persistence
    prediction
    monitoring
```

## Prerequisite

* Python

## Prepare Environment

```shell
python --version
pip --version
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

## LocalHost

## MLflow

```shell
cd ./ml_prediction
docker compose --file docker-compose.yml --project-name test up --build -d
```

```shell
cd ./ml_prediction
docker compose --file docker-compose.yml --project-name test down -v
rm ./mlflow.db
```

MLflow: [http://localhost:5000](http://localhost:5000)

### Interactive
```shell
cd ./ml_prediction
python -m ml_prediction.main
```

### Inline command
```shell
# single training
cd ./ml_prediction
# Test
pytest
# House
python -m ml_prediction.main house train
python -m ml_prediction.main house predict
# Online Shopping
python -m ml_prediction.main online_shopping train
python -m ml_prediction.main online_shopping predict
```


```shell
# Multi training
cd ./ml_prediction
# Test
pytest
# House
python -m ml_prediction.main house train --search
python -m ml_prediction.main house predict
# Online Shopping
python -m ml_prediction.main online_shopping train --search
python -m ml_prediction.main online_shopping predict
```

## Clean Project

```shell
cd ./ml_prediction
rm -rf ./src/*.egg-info
rm -rf ./models/*
rm -rf ./reports/*
rm -rf ./mlruns/*
rm ./mlflow.db
```
