from dataclasses import dataclass
from pathlib import Path

from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.audit_data import AuditData


@dataclass(frozen=True)
class ArtifactDto(AuditData):
    path: Path
    category: ArtifactCategory
