<h1 align="center">ML Prediction</h1>

Trains and runs a machine learning model for each registered dataset. `house` predicts the total price (regression)
and `online_shopping` predicts the order status (classification).

```text
Training
    load dataset
    build features and target
    split train, validation and test
    train (or search hyperparameters)
    evaluate validation and test
    save model and metadata
    record experiment and plots
    publish to MLflow

Prediction
    load model
    load dataset
    predict
    save predictions
```

## Project Structure

```text
ml_prediction
├── data/                     input datasets ({dataset}.csv)
├── models/                   trained models and their metadata
├── audit_log/                execution logs, experiments, plots and comparison charts
├── output/                   predictions
├── src/ml_prediction
│   ├── main.py               command line entry point
│   ├── config/               enums, dataset profiles and search grids
│   ├── model/                all dataclasses: settings, features, metrics, experiments, metadata
│   ├── estimator/            estimator and pipeline factory, hyperparameter search
│   ├── training/             trainer
│   ├── inference/            predictor
│   ├── repository/           dataset, data lake, model, experiment and prediction repositories
│   ├── audit/                execution log, experiments and MLflow
│   ├── visualize/            regression, classification and experiment plots
│   └── util/                 general helpers
└── tests
```

All commands below run from the repository root.

## 1. Prerequisite

* Python 3.12+
* Docker (for MLflow)

## 2. Prepare Environment

```shell
python --version
pip --version
docker --version
```

```shell
cd ./ml_prediction
python -m pip install --upgrade pip
pip install -r ./requirements.txt
pip install -e .
```

## 3. Test

```shell
cd ./ml_prediction
pytest
```

## 4. Start MLflow

MLflow is optional. Set `MLFLOW_ENABLED=true` and `MLFLOW_TRACKING_URI=http://localhost:5000` to publish runs.

```shell
cd ./ml_prediction
docker compose --file docker-compose.yml --project-name test up --build -d
```

MLflow: [http://localhost:5000](http://localhost:5000)

## 5. Run

Pass the dataset name and the operation (`train` or `predict`):

```shell
cd ./ml_prediction
python -m ml_prediction.main house train
python -m ml_prediction.main house predict
python -m ml_prediction.main online_shopping train
python -m ml_prediction.main online_shopping predict
```

Add `--search` to train with a hyperparameter search instead of the configured parameters:

```shell
cd ./ml_prediction
python -m ml_prediction.main house train --search
```

Without arguments, the command asks for both interactively. Predictions are written to `output/{dataset}_predictions.csv`.

### Configuration

| Variable                        | Default         | Description                                                                         |
|---------------------------------|-----------------|-------------------------------------------------------------------------------------|
| `ML_PREDICTION_DATASET_SOURCE`  | `local`         | `local` reads `data/{dataset}.csv`, `download` takes the latest data lake partition |
| `ML_PREDICTION_MODEL_TYPE`      | `random_forest` | `random_forest`, `extra_trees`, `gradient_boosting`, `hist_gradient_boosting`       |
| `ML_PREDICTION_SEARCH_ENABLED`  | `false`         | same as `--search`                                                                  |
| `ML_PREDICTION_VALIDATION_SIZE` | `0.2`           | validation share                                                                    |
| `ML_PREDICTION_TEST_SIZE`       | `0.2`           | test share                                                                          |
| `EXECUTION_LOG_ENABLED`         | `true`          | write `audit_log/{dataset}_{operation}_{run_id}.csv`                                |
| `EXPERIMENT_ENABLED`            | `true`          | append to `audit_log/{dataset}_experiments.csv`                                     |
| `MLFLOW_ENABLED`                | `false`         | publish training runs to MLflow                                                     |

## 6. Stop MLflow

```shell
cd ./ml_prediction
docker compose --file docker-compose.yml --project-name test down -v
```

## 7. Clean

```shell
cd ./ml_prediction
rm -rf ./src/*.egg-info
rm -rf ./models/* ./audit_log/* ./output/* ./mlruns/*
```
