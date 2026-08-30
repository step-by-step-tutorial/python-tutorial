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

### Interactive
```shell
cd ./ml_prediction
python -m ml_prediction.main
```

### Inline command
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