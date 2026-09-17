from dataclasses import dataclass
from typing import Any

from ml_prediction.audit.data.audit_data import AuditData


@dataclass(frozen=True)
class MetricsData(AuditData):
    prefix: str
    metrics: Any
