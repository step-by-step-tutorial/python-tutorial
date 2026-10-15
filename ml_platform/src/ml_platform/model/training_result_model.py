from dataclasses import dataclass

from sklearn.pipeline import Pipeline

from ml_platform.model.evaluation_model import EvaluationModel
from ml_platform.model.experiment_model import ExperimentModel


@dataclass(frozen=True)
class TrainingResultModel:
    experiment: ExperimentModel
    pipeline: Pipeline
    test_evaluation: EvaluationModel
