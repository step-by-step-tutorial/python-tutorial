from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType

SEARCH_PARAMETER_GRIDS: dict[ExperimentTaskType, dict[str, list]] = {
    ExperimentTaskType.CLASSIFICATION: {
        "classifier__n_estimators": [100, 300, 500],
        "classifier__max_depth": [None, 10, 20],
        "classifier__min_samples_split": [2, 4],
        "classifier__min_samples_leaf": [1, 2],
        "classifier__max_features": [0.7, 1.0],
    },
    ExperimentTaskType.REGRESSION: {
        "regressor__n_estimators": [100, 300, 500],
        "regressor__max_depth": [None, 10, 20],
        "regressor__min_samples_split": [2, 4],
        "regressor__min_samples_leaf": [1, 2],
        "regressor__max_features": [0.7, 1.0],
    },
}
