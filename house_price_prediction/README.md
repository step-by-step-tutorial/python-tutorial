# House Price Prediction

Initial machine-learning project for the house dataset.

The workflow downloads the latest CSV from the house data lake, prepares price-prediction features, trains a baseline
and Random Forest regression model, evaluates both, and saves the trained model.

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

The current implementation covers dataset preparation, feature engineering, train/test splitting, baseline modeling,
model training, evaluation, model persistence, and prediction. Monitoring is planned for a later phase.

## Project Structure

```text
src/house_price_prediction/
    config/
    dataset/
    features/
    model/
    training/
        trainer.py
        house_price_trainer.py
    evaluation/
    inference/
        predictor.py
        house_price_predictor.py
        prediction_service.py
    presentation/
        house_training_presenter.py
        house_prediction_presenter.py
    repository/
```

Generic trainers, predictors, and datasets define reusable contracts for future datasets. Services coordinate use cases,
while presenters handle logs and prediction output files. The CLI is limited to starting those workflows.

## Configuration

The downloader uses the existing house data lake settings by default:

```text
DATA_PLATFORM_HOUSE_DATALAKE_ENDPOINT=http://localhost:9000
DATA_PLATFORM_HOUSE_DATALAKE_ACCESS_KEY=admin
DATA_PLATFORM_HOUSE_DATALAKE_SECRET_KEY=administrator
DATA_PLATFORM_HOUSE_DATALAKE_BUCKET_NAME=house
HOUSE_ML_DATALAKE_PREFIX=
HOUSE_ML_DATA_DIR=data
HOUSE_ML_MODEL_DIR=models
HOUSE_ML_TARGET_COLUMN=total_price
HOUSE_ML_VALIDATION_SIZE=0.2
HOUSE_ML_TEST_SIZE=0.2
HOUSE_ML_RANDOM_STATE=42
```

`HOUSE_ML_DATALAKE_PREFIX` can restrict the search to a specific data lake path. The newest CSV under that prefix is
downloaded to `data/house.csv`.

## Run

```shell
pip install -e .
house-price-train
house-price-predict
```

Training uses a train/validation/test split, compares a mean-value baseline with a Random Forest model, and saves the
model to `models/house_price_model.joblib`. Prediction downloads the current CSV and writes
`data/house_predictions.csv`.
