import logging

from sklearn.model_selection import GridSearchCV, ParameterGrid
from sklearn.pipeline import Pipeline

from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.config.search_profiles import SEARCH_PARAMETER_GRIDS
from ml_prediction.model_selection.classification_selection import ClassificationSelection
from ml_prediction.pipeline.pipeline_step import PipelineStep

logger = logging.getLogger(__name__)


class ClassificationModelSelector:
    def __init__(self, cross_validation_folds: int = 3, n_jobs: int = -1) -> None:
        self._cross_validation_folds = cross_validation_folds
        self._n_jobs = n_jobs

    def select(self, pipeline: Pipeline, features, target) -> ClassificationSelection:
        parameter_grid = SEARCH_PARAMETER_GRIDS[ExperimentTaskType.CLASSIFICATION]
        candidate_count = len(list(ParameterGrid(parameter_grid)))
        logger.info(
            f"Classification model search started: "
            f"candidates={candidate_count} "
            f"cross_validation_folds={self._cross_validation_folds} "
            f"metric=f1_weighted"
        )
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=parameter_grid,
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
                key.removeprefix(f"{PipelineStep.CLASSIFIER}__"): value
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
                key.removeprefix(f"{PipelineStep.CLASSIFIER}__"): value
                for key, value in search.best_params_.items()
            },
            search.best_score_,
        )
        return ClassificationSelection(
            pipeline=search.best_estimator_,
            parameters=dict(search.best_params_),
            f1_score=float(search.best_score_),
        )
