import pytest

from ml_prediction.config.model_type import ModelType
from ml_prediction.config.pipeline_step import PipelineStep
from ml_prediction.config.dataset_profiles import HOUSE
from ml_prediction.config.task_type import TaskType
from ml_prediction.estimator.pipeline_factory import create_estimator, create_pipeline
from ml_prediction.model.settings_model import ModelParametersModel


def test_create_estimator_passes_only_supported_parameters() -> None:
    estimator = create_estimator(TaskType.REGRESSION, ModelType.HIST_GRADIENT_BOOSTING,
                                 ModelParametersModel(max_depth=5, random_state=7))

    parameters = estimator.get_params()
    assert parameters["max_depth"] == 5
    assert parameters["random_state"] == 7
    assert "n_estimators" not in parameters


def test_create_estimator_rejects_unsupported_model_type() -> None:
    with pytest.raises(ValueError, match="Unsupported classification model type"):
        create_estimator(TaskType.CLASSIFICATION, ModelType.EXTRA_TREES, ModelParametersModel())


def test_create_pipeline_has_preprocessor_and_estimator_steps() -> None:
    estimator = create_estimator(TaskType.REGRESSION, ModelType.RANDOM_FOREST, ModelParametersModel())

    pipeline = create_pipeline(HOUSE.features, estimator)

    assert [name for name, _ in pipeline.steps] == [PipelineStep.PREPROCESSOR, PipelineStep.ESTIMATOR]
    assert pipeline.named_steps[PipelineStep.ESTIMATOR] is estimator
