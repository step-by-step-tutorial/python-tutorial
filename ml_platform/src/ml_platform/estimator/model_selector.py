import logging
from typing import Any

from sklearn.model_selection import GridSearchCV, ParameterGrid
from sklearn.pipeline import Pipeline

from ml_platform.config.model_type import ModelType
from ml_platform.config.pipeline_step import PipelineStep
from ml_platform.config.search_grid import SEARCH_GRIDS
from ml_platform.config.task_type import TaskType
from ml_platform.model.dataset_split_model import FeaturesAndTargetModel
from ml_platform.model.selection_model import SelectionModel

logger = logging.getLogger(__name__)

PARAMETER_PREFIX = f"{PipelineStep.ESTIMATOR}__"

# scikit-learn maximizes the score, so error metrics are negated: (scoring, reported metric, sign).
SCORING: dict[TaskType, tuple[str, str, int]] = {
    TaskType.REGRESSION: ("neg_mean_absolute_error", "mean_absolute_error", -1),
    TaskType.CLASSIFICATION: ("f1_weighted", "f1_weighted", 1),
}


def _strip_prefix(parameters: dict[str, Any]) -> dict[str, Any]:
    return {name.removeprefix(PARAMETER_PREFIX): value for name, value in parameters.items()}


class ModelSelector:
    def __init__(self, cross_validation_folds: int = 3, n_jobs: int = -1) -> None:
        self._cross_validation_folds = cross_validation_folds
        self._n_jobs = n_jobs

    def select(
            self,
            pipeline: Pipeline,
            data: FeaturesAndTargetModel,
            task_type: TaskType,
            model_type: ModelType,
    ) -> SelectionModel:
        scoring, metric, sign = SCORING[task_type]
        parameter_grid = {f"{PARAMETER_PREFIX}{name}": values for name, values in SEARCH_GRIDS[model_type].items()}
        candidate_count = len(ParameterGrid(parameter_grid))
        logger.info("Model search started: candidates=%s folds=%s metric=%s", candidate_count,
                    self._cross_validation_folds, metric)

        search = GridSearchCV(
            estimator=pipeline,
            param_grid=parameter_grid,
            scoring=scoring,
            cv=self._cross_validation_folds,
            n_jobs=self._n_jobs,
            refit=True,
        )
        search.fit(data.features, data.target)

        results = zip(search.cv_results_["params"], search.cv_results_["mean_test_score"], strict=True)
        for index, (parameters, score) in enumerate(results, start=1):
            logger.info("Model search candidate %s/%s: parameters=%s %s=%.4f", index, candidate_count,
                        _strip_prefix(parameters), metric, sign * score)

        selection = SelectionModel(
            pipeline=search.best_estimator_,
            parameters=_strip_prefix(search.best_params_),
            metric=metric,
            score=float(sign * search.best_score_),
        )
        logger.info("Model search completed: parameters=%s %s=%.4f", selection.parameters, metric, selection.score)
        return selection
