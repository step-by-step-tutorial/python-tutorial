from sklearn.base import RegressorMixin
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)

from ml_prediction.config.settings import get_settings

model_types = ("random_forest", "extra_trees", "gradient_boosting", "hist_gradient_boosting",)


class RegressorBuilder:
    def __init__(self, dataset_name: str) -> None:
        self._dataset_name = dataset_name

    def build(self) -> RegressorMixin:
        settings = get_settings(self._dataset_name)
        if settings.model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=settings.n_estimators,
                max_depth=settings.max_depth,
                min_samples_split=settings.min_samples_split,
                min_samples_leaf=settings.min_samples_leaf,
                max_features=settings.max_features,
                bootstrap=settings.bootstrap,
                random_state=settings.random_state,
                n_jobs=settings.n_jobs,
            )
        elif settings.model_type == "extra_trees":
            return ExtraTreesRegressor(
                n_estimators=settings.n_estimators,
                max_depth=settings.max_depth,
                min_samples_split=settings.min_samples_split,
                min_samples_leaf=settings.min_samples_leaf,
                max_features=settings.max_features,
                bootstrap=settings.bootstrap,
                random_state=settings.random_state,
                n_jobs=settings.n_jobs,
            )
        elif settings.model_type == "gradient_boosting":
            return GradientBoostingRegressor(
                n_estimators=settings.n_estimators,
                max_depth=settings.max_depth,
                min_samples_split=settings.min_samples_split,
                min_samples_leaf=settings.min_samples_leaf,
                max_features=settings.max_features,
                random_state=settings.random_state,
            )
        elif settings.model_type == "hist_gradient_boosting":
            return HistGradientBoostingRegressor(
                max_depth=settings.max_depth,
                min_samples_leaf=settings.min_samples_leaf,
                max_features=settings.max_features,
                random_state=settings.random_state,
            )
        else:
            raise Exception(
                f"Unsupported model type: {settings.model_type}. Supported model types: {', '.join(model_types)}")
