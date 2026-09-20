from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.data.audit_data import AuditData


@dataclass(frozen=True)
class PipelineStepDto(AuditData):
    step: ClassVar[str]

    def to_dict(self) -> dict[str, Any]:
        return {}
