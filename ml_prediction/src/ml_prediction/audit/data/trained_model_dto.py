from dataclasses import dataclass
from typing import Any

from ml_prediction.audit.data.audit_data import AuditData


@dataclass(frozen=True)
class TrainedModelDto(AuditData):
    model: Any
