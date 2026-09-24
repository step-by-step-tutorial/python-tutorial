from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.pipeline.pipeline_step import PipelineStep

SEARCH_PARAMETER_GRIDS: dict[ExperimentTaskType, dict[str, list]] = {
    ExperimentTaskType.CLASSIFICATION: {
        f"{PipelineStep.CLASSIFIER}__n_estimators": [100, 300, 500],
        f"{PipelineStep.CLASSIFIER}__max_depth": [None, 10, 20],
        f"{PipelineStep.CLASSIFIER}__min_samples_split": [2, 4],
        f"{PipelineStep.CLASSIFIER}__min_samples_leaf": [1, 2],
        f"{PipelineStep.CLASSIFIER}__max_features": [0.7, 1.0],
    },
    ExperimentTaskType.REGRESSION: {
        f"{PipelineStep.REGRESSOR}__n_estimators": [100, 300, 500],
        f"{PipelineStep.REGRESSOR}__max_depth": [None, 10, 20],
        f"{PipelineStep.REGRESSOR}__min_samples_split": [2, 4],
        f"{PipelineStep.REGRESSOR}__min_samples_leaf": [1, 2],
        f"{PipelineStep.REGRESSOR}__max_features": [0.7, 1.0],
    },
}
