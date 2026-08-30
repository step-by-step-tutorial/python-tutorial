from sklearn.base import RegressorMixin
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)


class RegressorBuilder:
    def __init__(
            self,
            model_type: str,
            n_estimators: int,
            n_jobs: int,
            random_state: int,
            max_depth: int | None = None,
            min_samples_split: int = 2,
            min_samples_leaf: int = 1,
            max_features: int | float | str | None = 1.0,
            bootstrap: bool = True,
    ) -> None:
        self._model_type = model_type
        self._n_estimators = n_estimators
        self._n_jobs = n_jobs
        self._random_state = random_state
        self._max_depth = max_depth
        self._min_samples_split = min_samples_split
        self._min_samples_leaf = min_samples_leaf
        self._max_features = max_features
        self._bootstrap = bootstrap

    def build(self) -> RegressorMixin:
        if self._model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=self._n_estimators,
                max_depth=self._max_depth,
                min_samples_split=self._min_samples_split,
                min_samples_leaf=self._min_samples_leaf,
                max_features=self._max_features,
                bootstrap=self._bootstrap,
                random_state=self._random_state,
                n_jobs=self._n_jobs,
            )
        if self._model_type == "extra_trees":
            return ExtraTreesRegressor(
                n_estimators=self._n_estimators,
                max_depth=self._max_depth,
                min_samples_split=self._min_samples_split,
                min_samples_leaf=self._min_samples_leaf,
                max_features=self._max_features,
                bootstrap=self._bootstrap,
                random_state=self._random_state,
                n_jobs=self._n_jobs,
            )
        if self._model_type == "gradient_boosting":
            return GradientBoostingRegressor(
                n_estimators=self._n_estimators,
                max_depth=self._max_depth,
                min_samples_split=self._min_samples_split,
                min_samples_leaf=self._min_samples_leaf,
                max_features=self._max_features,
                random_state=self._random_state,
            )
        if self._model_type == "hist_gradient_boosting":
            return HistGradientBoostingRegressor(
                max_depth=self._max_depth,
                min_samples_leaf=self._min_samples_leaf,
                max_features=self._max_features,
                random_state=self._random_state,
            )

        supported_model_types = (
            "random_forest",
            "extra_trees",
            "gradient_boosting",
            "hist_gradient_boosting",
        )
        raise ValueError(
            f"Unsupported model type: {self._model_type}. "
            f"Supported model types: {', '.join(supported_model_types)}"
        )
