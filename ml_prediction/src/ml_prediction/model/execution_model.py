import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ExecutionModel:
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
    metrics: dict[str, float] = field(default_factory=dict)
    details: str = ""

    @classmethod
    def from_dict(cls, values: dict[str, str]) -> "ExecutionModel":
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
            metrics=json.loads(values.get("metrics") or "{}"),
            details=values.get("details", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
            "metrics": json.dumps(self.metrics, sort_keys=True, separators=(",", ":")),
        }
