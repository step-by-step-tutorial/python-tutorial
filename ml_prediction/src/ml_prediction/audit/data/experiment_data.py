import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.data_model.metrics import Metrics
from ml_prediction.utils.metrics_utils import create_metrics


@dataclass(frozen=True)
class ExperimentData(AuditData):
    experiment_id: str
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
    run_id: str = ""
    task_type: ExperimentTaskType = ExperimentTaskType.REGRESSION

    def to_dict(self) -> dict[str, str | float]:
        return {
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "dataset_name": self.dataset_name,
            "task_type": self.task_type.value,
            "model_type": self.model_type,
            "model_parameters": json.dumps(self.model_parameters, sort_keys=True, separators=(",", ":")),
            "model_selection_metric": self.model_selection_metric or "",
            "model_selection_score": self.model_selection_score if self.model_selection_score is not None else "",
            "validation_metrics": json.dumps({key: float(value) for key, value in asdict(self.validation_metrics).items()}),
            "test_metrics": json.dumps({key: float(value) for key, value in asdict(self.test_metrics).items()}),
            "model_path": str(self.model_path),
            "audit_path": str(self.audit_path) if self.audit_path is not None else "",
        }

    @staticmethod
    def from_row(row: dict[str, str]) -> "ExperimentData":
        task_type = ExperimentTaskType.value_of(row["task_type"])
        metric_type = task_type.metrics_type
        return ExperimentData(
            experiment_id=row["experiment_id"],
            run_id=row.get("run_id", ""),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            dataset_name=row["dataset_name"],
            task_type=task_type,
            model_type=row["model_type"],
            model_parameters=json.loads(row["model_parameters"]),
            validation_metrics=create_metrics(json.loads(row["validation_metrics"]), metric_type),
            test_metrics=create_metrics(json.loads(row["test_metrics"]), metric_type),
            model_path=Path(row["model_path"]),
            audit_path=Path(row["audit_path"]) if row.get("audit_path") else None,
            model_selection_metric=row.get("model_selection_metric") or None,
            model_selection_score=float(row["model_selection_score"]) if row.get("model_selection_score") else None,
        )
