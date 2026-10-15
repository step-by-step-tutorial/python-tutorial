<h1 align="center">ML Platform</h1>

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
ml_platform
├── data/                     input datasets ({dataset}.csv)
├── models/                   trained models and their metadata
├── audit_log/                execution logs, experiments, plots and comparison charts
├── output/                   predictions
├── src/ml_platform
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
* Docker, for MLflow

```shell
python --version
pip --version
docker --version
```

## 2. Install

```shell
python -m pip install --upgrade pip
pip install -r ./ml_platform/requirements.txt
pip install -e ./ml_platform
```

## 3. Test

```shell
pytest ./ml_platform
```

## 4. Start MLflow

MLflow is optional. Set `MLFLOW_ENABLED=true` and `MLFLOW_TRACKING_URI=http://localhost:5000` to publish runs.

```shell
docker compose --file ./ml_platform/docker-compose.yml --project-name test up --build -d
```

MLflow: [http://localhost:5000](http://localhost:5000)

## 5. Run

Pass the dataset name and the operation (`train` or `predict`):

```shell
python -m ml_platform.main house train
python -m ml_platform.main house predict
python -m ml_platform.main online_shopping train
python -m ml_platform.main online_shopping predict
```

Add `--search` to train with a hyperparameter search instead of the configured parameters:

```shell
python -m ml_platform.main house train --search
```

Without arguments, the command asks for both interactively. Predictions are written to `output/{dataset}_predictions.csv`.

### 5.1. Configuration

| Variable                        | Default         | Description                                                                         |
|---------------------------------|-----------------|-------------------------------------------------------------------------------------|
| `ML_PLATFORM_DATASET_SOURCE`  | `local`         | `local` reads `data/{dataset}.csv`, `download` takes the latest data lake partition |
| `ML_PLATFORM_MODEL_TYPE`      | `random_forest` | `random_forest`, `extra_trees`, `gradient_boosting`, `hist_gradient_boosting`       |
| `ML_PLATFORM_SEARCH_ENABLED`  | `false`         | same as `--search`                                                                  |
| `ML_PLATFORM_VALIDATION_SIZE` | `0.2`           | validation share                                                                    |
| `ML_PLATFORM_TEST_SIZE`       | `0.2`           | test share                                                                          |
| `EXECUTION_LOG_ENABLED`         | `true`          | write `audit_log/{dataset}_{operation}_{run_id}.csv`                                |
| `EXPERIMENT_ENABLED`            | `true`          | append to `audit_log/{dataset}_experiments.csv`                                     |
| `MLFLOW_ENABLED`                | `false`         | publish training runs to MLflow                                                     |

## 6. Stop MLflow

```shell
docker compose --file ./ml_platform/docker-compose.yml --project-name test down -v
```

## 7. Clean

```shell
rm -rf ./ml_platform/src/*.egg-info
rm -rf ./ml_platform/models/* ./ml_platform/audit_log/* ./ml_platform/output/* ./ml_platform/mlruns/*
```
