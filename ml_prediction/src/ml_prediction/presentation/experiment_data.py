from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from ml_prediction.audit.artifact_data import ArtifactData
from ml_prediction.audit.experiment import Experiment
from ml_prediction.data_model.classification_evaluation import ClassificationEvaluation
from ml_prediction.data_model.evaluation import RegressionEvaluation

Evaluation = RegressionEvaluation | ClassificationEvaluation


@dataclass(frozen=True)
class ExperimentData:
    """Context shared by CLI, visual, and web presenters."""

    experiment: Experiment | None = None
    model: object | None = None
    evaluation: Evaluation | None = None
    report_dir: Path | None = None
    metrics: Mapping[str, float] | None = None
    artifacts: tuple[ArtifactData, ...] = ()
