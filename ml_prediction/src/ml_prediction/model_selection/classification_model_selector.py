import logging
from dataclasses import dataclass
from typing import Any

from sklearn.model_selection import GridSearchCV, ParameterGrid
from sklearn.pipeline import Pipeline

from ml_prediction.config.classification_search import CLASSIFICATION_PARAMETER_GRID

logger = logging.getLogger(__name__)


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
        candidate_count = len(list(ParameterGrid(CLASSIFICATION_PARAMETER_GRID)))
        logger.info(
            "Classification model search started: candidates=%s cross_validation_folds=%s metric=f1_weighted",
            candidate_count,
            self._cross_validation_folds,
        )
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=CLASSIFICATION_PARAMETER_GRID,
            scoring="f1_weighted",
            cv=self._cross_validation_folds,
            n_jobs=self._n_jobs,
            refit=True,
        )
        search.fit(features, target)
        for index, (parameters, score) in enumerate(
                zip(search.cv_results_["params"], search.cv_results_["mean_test_score"], strict=True),
                start=1,
        ):
            readable_parameters = {
                key.removeprefix("classifier__"): value
                for key, value in parameters.items()
            }
            logger.info(
                "Classification model search candidate %s/%s: parameters=%s validation_f1_weighted=%.4f",
                index,
                candidate_count,
                readable_parameters,
                score,
            )
        logger.info(
            "Classification model search completed: best_parameters=%s cross_validation_f1_weighted=%.4f",
            {
                key.removeprefix("classifier__"): value
                for key, value in search.best_params_.items()
            },
            search.best_score_,
        )
        return ClassificationSelection(
            pipeline=search.best_estimator_,
            parameters=dict(search.best_params_),
            f1_score=float(search.best_score_),
        )
