from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ml_platform.config.model_type import ModelType
from ml_platform.config.pipeline_step import PipelineStep
from ml_platform.config.task_type import TaskType
from ml_platform.model.feature_set_model import FeatureSetModel
from ml_platform.model.settings_model import ModelParametersModel

ESTIMATORS: dict[TaskType, dict[ModelType, type[BaseEstimator]]] = {
    TaskType.REGRESSION: {
        ModelType.RANDOM_FOREST: RandomForestRegressor,
        ModelType.EXTRA_TREES: ExtraTreesRegressor,
        ModelType.GRADIENT_BOOSTING: GradientBoostingRegressor,
        ModelType.HIST_GRADIENT_BOOSTING: HistGradientBoostingRegressor,
    },
    TaskType.CLASSIFICATION: {
        ModelType.RANDOM_FOREST: RandomForestClassifier,
    },
}


def create_estimator(task_type: TaskType, model_type: ModelType, parameters: ModelParametersModel) -> BaseEstimator:
    estimators = ESTIMATORS[task_type]
    if model_type not in estimators:
        supported = ", ".join(estimators)
        raise ValueError(f"Unsupported {task_type} model type: {model_type}. Supported model types: {supported}")

    estimator_class = estimators[model_type]
    # Each estimator accepts a different subset of the configured parameters.
    supported_parameters = estimator_class().get_params()
    return estimator_class(**{
        name: value for name, value in parameters.to_dict().items() if name in supported_parameters
    })


def create_pipeline(features: FeatureSetModel, estimator: BaseEstimator) -> Pipeline:
    numeric_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric_transformer, list(features.numeric + features.boolean)),
        ("categorical", categorical_transformer, list(features.categorical)),
    ])
    return Pipeline([
        (PipelineStep.PREPROCESSOR, preprocessor),
        (PipelineStep.ESTIMATOR, estimator),
    ])
