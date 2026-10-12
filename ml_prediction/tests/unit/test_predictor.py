import pandas as pd

from ml_prediction.config.operation import Operation
from ml_prediction.inference.predictor import Predictor
from ml_prediction.model.execution_model import ExecutionModel
from ml_prediction.training.trainer import Trainer
from ml_prediction.util.csv_utils import read_rows


def prediction_run_id(settings) -> str:
    log = next(settings.audit_dir.glob(f"{settings.dataset_name}_{Operation.PREDICT}_*.csv"))
    return log.stem.removeprefix(f"{settings.dataset_name}_{Operation.PREDICT}_")


def test_predict_writes_predictions(house_settings) -> None:
    Trainer(house_settings).train()

    prediction = Predictor(house_settings).predict()

    output = pd.read_csv(house_settings.prediction_path)
    assert house_settings.profile.prediction_column in output.columns
    assert len(output) == len(prediction.dataframe)
    executions = read_rows(house_settings.execution_log_path(Operation.PREDICT, prediction_run_id(house_settings)),
                           ExecutionModel.from_dict)
    assert [execution.step for execution in executions] == [
        "model_loaded", "dataset_loaded", "predictions_generated", "prediction_saved",
    ]


def test_predict_classification(online_shopping_settings) -> None:
    Trainer(online_shopping_settings).train()

    Predictor(online_shopping_settings).predict()

    output = pd.read_csv(online_shopping_settings.prediction_path)
    assert set(output[online_shopping_settings.profile.prediction_column]) <= {"Delivered", "Cancelled"}
