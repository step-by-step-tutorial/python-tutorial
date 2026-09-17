from dataclasses import dataclass
from pathlib import Path

from ml_prediction.audit.data.audit_data import AuditData


@dataclass(frozen=True)
class ArtifactData(AuditData):
    path: Path
    category: str
