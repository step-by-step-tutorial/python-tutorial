from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.data_model.classification_evaluation_data import ClassificationEvaluationData
from ml_prediction.data_model.evaluation_data import RegressionEvaluationData

@dataclass(frozen=True)
class ExperimentAuditData(AuditData):
    experiment: ExperimentData | None = None
    model: object | None = None
    evaluation: RegressionEvaluationData | ClassificationEvaluationData | None = None
    audit_dir: Path | None = None
    metrics: Mapping[str, float] = field(default_factory=dict)
    artifacts: tuple[ArtifactData, ...] = ()
