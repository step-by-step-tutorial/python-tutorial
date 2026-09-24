from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_dto import ExperimentDto
from ml_prediction.data_model.evaluation_dto import EvaluationDto


@dataclass(frozen=True)
class TrainingAuditDto(AuditData):
    experiment: ExperimentDto | None = None
    model: object | None = None
    evaluation: EvaluationDto | None = None
    path: Path | None = None
    metrics: Mapping[str, float] = field(default_factory=dict)
    artifacts: tuple[ArtifactDto, ...] = ()
