from dataclasses import dataclass
from typing import Any

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from ml_prediction.config.regression_search import REGRESSION_PARAMETER_GRID


@dataclass(frozen=True)
class RegressionSelection:
    pipeline: Pipeline
    parameters: dict[str, Any]
    mean_absolute_error: float


class RegressionModelSelector:
    def __init__(self, cross_validation_folds: int = 3, n_jobs: int = -1) -> None:
        self._cross_validation_folds = cross_validation_folds
        self._n_jobs = n_jobs

    def select(self, pipeline: Pipeline, features, target) -> RegressionSelection:
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=REGRESSION_PARAMETER_GRID,
            scoring="neg_mean_absolute_error",
            cv=self._cross_validation_folds,
            n_jobs=self._n_jobs,
            refit=True,
        )
        search.fit(features, target)
        return RegressionSelection(
            pipeline=search.best_estimator_,
            parameters=dict(search.best_params_),
            mean_absolute_error=float(-search.best_score_),
        )
