from dataclasses import dataclass
from typing import Any

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from ml_prediction.config.classification_search import CLASSIFICATION_PARAMETER_GRID


@dataclass(frozen=True)
class ClassificationSelection:
    pipeline: Pipeline
    parameters: dict[str, Any]
    f1_score: float


class ClassificationModelSelector:
    def __init__(self, cross_validation_folds: int = 3, n_jobs: int = -1) -> None:
        self._cross_validation_folds = cross_validation_folds
        self._n_jobs = n_jobs

    def select(self, pipeline: Pipeline, features, target) -> ClassificationSelection:
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=CLASSIFICATION_PARAMETER_GRID,
            scoring="f1_weighted",
            cv=self._cross_validation_folds,
            n_jobs=self._n_jobs,
            refit=True,
        )
        search.fit(features, target)
        return ClassificationSelection(
            pipeline=search.best_estimator_,
            parameters=dict(search.best_params_),
            f1_score=float(search.best_score_),
        )
