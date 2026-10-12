import pytest

from conftest import make_settings, write_dataset
from ml_prediction.audit import audit_service
from ml_prediction.config.dataset_profiles import HOUSE
from ml_prediction.config.model_type import ModelType
from ml_prediction.config.operation import Operation
from ml_prediction.model.execution_model import ExecutionModel
from ml_prediction.model.metrics_model import ClassificationMetricsModel, RegressionMetricsModel
from ml_prediction.model.settings_model import MlflowSettingsModel
from ml_prediction.repository.experiment_repository import ExperimentRepository
from ml_prediction.repository.model_repository import ModelRepository
from ml_prediction.training.trainer import Trainer
from ml_prediction.util.csv_utils import read_rows

TRAINING_STEPS = [
    "dataset_loaded",
    "features_built",
    "target_extracted",
    "dataset_split",
    "model_trained",
    "model_evaluated",
    "model_evaluated",
    "model_saved",
]


def executed_steps(settings, run_id: str) -> list[str]:
    path = settings.execution_log_path(Operation.TRAIN, run_id)
    return [execution.step for execution in read_rows(path, ExecutionModel.from_dict)]


def test_train_regression_saves_model_experiment_and_plots(house_settings) -> None:
    result = Trainer(house_settings).train()

    experiment = result.experiment
    assert isinstance(experiment.test_metrics, RegressionMetricsModel)
    assert ModelRepository().load_metadata(house_settings.model_path).run_id == experiment.run_id
    assert ExperimentRepository(house_settings.experiment_path).find_all() == [experiment]
    assert executed_steps(house_settings, experiment.run_id) == TRAINING_STEPS
    assert house_settings.artifact_path(experiment.run_id, "actual_vs_predicted.png").exists()
    assert house_settings.artifact_path(experiment.run_id, "feature_importance.png").exists()
    assert house_settings.comparison_path("validation_mae.png").exists()


def test_train_classification(online_shopping_settings) -> None:
    result = Trainer(online_shopping_settings).train()

    assert isinstance(result.experiment.test_metrics, ClassificationMetricsModel)
    assert online_shopping_settings.model_path.exists()
    assert online_shopping_settings.artifact_path(result.experiment.run_id, "confusion_matrix.png").exists()


def test_train_without_feature_importance(tmp_path) -> None:
    settings = make_settings(tmp_path, HOUSE, model_type=ModelType.HIST_GRADIENT_BOOSTING)
    write_dataset(settings)

    result = Trainer(settings).train()

    assert settings.model_path.exists()
    assert not settings.artifact_path(result.experiment.run_id, "feature_importance.png").exists()


def test_train_publishes_to_mlflow_when_enabled(tmp_path, mocker) -> None:
    settings = make_settings(tmp_path, HOUSE, mlflow=MlflowSettingsModel(enabled=True))
    write_dataset(settings)
    mlflow_service = mocker.patch.object(audit_service, "MlflowService")

    result = Trainer(settings).train()

    result_argument, artifacts = mlflow_service.return_value.publish.call_args.args
    assert result_argument is result
    assert artifacts


def test_train_with_unknown_target_column_fails(tmp_path) -> None:
    settings = make_settings(tmp_path, HOUSE)
    write_dataset(settings).drop(columns=HOUSE.target_column).to_csv(settings.dataset_path, index=False)

    with pytest.raises(KeyError):
        Trainer(settings).train()
