from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ExecutionModel:
    timestamp: datetime
    run_id: str
    task_name: str
    step: str
    rows: int | None
    details: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "run_id": self.run_id,
            "task_name": self.task_name,
            "step": self.step,
            "rows": "" if self.rows is None else self.rows,
            "details": self.details,
        }
