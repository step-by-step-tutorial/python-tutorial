import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Self

from ml_prediction.audit.data.audit_data import AuditData


@dataclass(frozen=True)
class ExecutionLog(AuditData):
    timestamp: datetime
    run_id: str
    dataset_name: str
    operation: str
    step: str
    partition: str = ""
    rows: int | None = None
    model_name: str = ""
    model_path: str = ""
    model_id: str = ""
    metrics: dict[str, float] | None = None
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        values = asdict(self)
        values["timestamp"] = self.timestamp.isoformat()
        values["metrics"] = json.dumps(self.metrics or {}, sort_keys=True, separators=(",", ":"))
        return values

    @classmethod
    def from_dict(cls: type[Self], values: dict[str, str]) -> Self:
        return cls(
            timestamp=datetime.fromisoformat(values["timestamp"]),
            run_id=values["run_id"],
            dataset_name=values["dataset_name"],
            operation=values["operation"],
            step=values["step"],
            partition=values.get("partition", ""),
            rows=int(values["rows"]) if values.get("rows") else None,
            model_name=values.get("model_name", ""),
            model_path=values.get("model_path", ""),
            model_id=values.get("model_id", ""),
            metrics=json.loads(values.get("metrics", "{}")),
            details=values.get("details", ""),
        )
