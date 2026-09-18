from dataclasses import dataclass
from pathlib import Path

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.artifact_category import ArtifactCategory


@dataclass(frozen=True)
class ArtifactData(AuditData):
    path: Path
    category: ArtifactCategory
