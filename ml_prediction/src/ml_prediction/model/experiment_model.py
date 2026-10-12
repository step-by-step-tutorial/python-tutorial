import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ml_prediction.config.task_type import TaskType
from ml_prediction.model.metrics_model import MetricsModel


def _to_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class ExperimentModel:
    run_id: str
    timestamp: datetime
    dataset_name: str
    task_type: TaskType
    model_type: str
    model_parameters: dict[str, Any]
    validation_metrics: MetricsModel
    test_metrics: MetricsModel
    model_path: Path
    selection_metric: str | None = None
    selection_score: float | None = None

    @classmethod
    def from_dict(cls, values: dict[str, str]) -> "ExperimentModel":
        task_type = TaskType(values["task_type"])
        metrics_type = MetricsModel.type_of(task_type)
        return cls(
            run_id=values["run_id"],
            timestamp=datetime.fromisoformat(values["timestamp"]),
            dataset_name=values["dataset_name"],
            task_type=task_type,
            model_type=values["model_type"],
            model_parameters=json.loads(values["model_parameters"]),
            validation_metrics=metrics_type.from_dict(json.loads(values["validation_metrics"])),
            test_metrics=metrics_type.from_dict(json.loads(values["test_metrics"])),
            model_path=Path(values["model_path"]),
            selection_metric=values.get("selection_metric") or None,
            selection_score=float(values["selection_score"]) if values.get("selection_score") else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "dataset_name": self.dataset_name,
            "task_type": self.task_type.value,
            "model_type": self.model_type,
            "model_parameters": _to_json(self.model_parameters),
            "validation_metrics": _to_json(self.validation_metrics.to_dict()),
            "test_metrics": _to_json(self.test_metrics.to_dict()),
            "model_path": str(self.model_path),
            "selection_metric": self.selection_metric or "",
            "selection_score": "" if self.selection_score is None else self.selection_score,
        }

    def to_metrics(self) -> dict[str, float]:
        return {
            **{f"validation_{key}": value for key, value in self.validation_metrics.to_dict().items()},
            **{f"test_{key}": value for key, value in self.test_metrics.to_dict().items()},
        }
