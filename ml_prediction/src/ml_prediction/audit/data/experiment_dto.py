import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Self

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.data_model.metrics import Metrics
from ml_prediction.utils.metrics_utils import create_metrics


@dataclass(frozen=True)
class ExperimentDto(AuditData):
    run_id: str
    timestamp: datetime
    dataset_name: str
    model_type: str
    model_parameters: dict[str, Any]
    validation_metrics: Metrics
    test_metrics: Metrics
    model_path: Path
    audit_path: Path | None
    model_selection_metric: str | None = None
    model_selection_score: float | None = None
    task_type: ExperimentTaskType = ExperimentTaskType.UNKNOWN

    def to_string(self) -> str:
        return (
            f"run_id={self.run_id} "
            f"dataset={self.dataset_name} "
            f"model_type={self.model_type}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "dataset_name": self.dataset_name,
            "task_type": self.task_type.value,
            "model_type": self.model_type,
            "model_parameters": json.dumps(self.model_parameters, sort_keys=True, separators=(",", ":")),
            "model_selection_metric": self.model_selection_metric or "",
            "model_selection_score": self.model_selection_score if self.model_selection_score is not None else "",
            "validation_metrics": json.dumps(
                {key: float(value) for key, value in asdict(self.validation_metrics).items()}),
            "test_metrics": json.dumps({key: float(value) for key, value in asdict(self.test_metrics).items()}),
            "model_path": str(self.model_path),
            "audit_path": str(self.audit_path) if self.audit_path is not None else "",
        }

    @classmethod
    def from_dict(cls: type[Self], values: dict[str, Any]) -> Self:
        task_type = ExperimentTaskType.value_of(values["task_type"])
        metric_type = task_type.metrics_type
        return cls(
            run_id=values["run_id"],
            timestamp=datetime.fromisoformat(values["timestamp"]),
            dataset_name=values["dataset_name"],
            task_type=task_type,
            model_type=values["model_type"],
            model_parameters=json.loads(values["model_parameters"]),
            validation_metrics=create_metrics(json.loads(values["validation_metrics"]), metric_type),
            test_metrics=create_metrics(json.loads(values["test_metrics"]), metric_type),
            model_path=Path(values["model_path"]),
            audit_path=Path(values["audit_path"]) if values.get("audit_path") else None,
            model_selection_metric=values.get("model_selection_metric") or None,
            model_selection_score=float(values["model_selection_score"])
            if values.get("model_selection_score")
            else None,
        )
