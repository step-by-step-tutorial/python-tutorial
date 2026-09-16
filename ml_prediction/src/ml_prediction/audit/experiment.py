import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Experiment:
    fieldnames = ("experiment_id", "run_id", "timestamp", "dataset_name", "task_type", "model_type", "model_parameters",
                  "model_selection_metric", "model_selection_score", "validation_metrics", "test_metrics", "model_path",
                  "report_path")
    experiment_id: str
    timestamp: datetime
    dataset_name: str
    model_type: str
    model_parameters: dict[str, Any]
    validation_metrics: Any
    test_metrics: Any
    model_path: Path
    report_path: Path | None
    model_selection_metric: str | None = None
    model_selection_score: float | None = None
    run_id: str = ""
    task_type: str = "regression"

    def to_row(self) -> dict[str, str | float]:
        from ml_prediction.audit.models import metrics_to_dict
        return {
            "experiment_id": self.experiment_id, "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(), "dataset_name": self.dataset_name,
            "task_type": self.task_type, "model_type": self.model_type,
            "model_parameters": json.dumps(self.model_parameters, sort_keys=True, separators=(",", ":")),
            "model_selection_metric": self.model_selection_metric or "",
            "model_selection_score": self.model_selection_score if self.model_selection_score is not None else "",
            "validation_metrics": json.dumps(metrics_to_dict(self.validation_metrics)),
            "test_metrics": json.dumps(metrics_to_dict(self.test_metrics)),
            "model_path": str(self.model_path), "report_path": str(self.report_path or ""),
        }

    @staticmethod
    def from_row(row: dict[str, str]) -> "Experiment":
        from ml_prediction.audit.models import metrics_from_dict
        task_type = row.get("task_type") or "regression"
        return Experiment(
            row["experiment_id"], datetime.fromisoformat(row["timestamp"]), row["dataset_name"],
            row["model_type"], json.loads(row["model_parameters"]),
            metrics_from_dict(json.loads(row["validation_metrics"]), task_type),
            metrics_from_dict(json.loads(row["test_metrics"]), task_type), Path(row["model_path"]),
            Path(row["report_path"]) if row.get("report_path") else None,
            row.get("model_selection_metric") or None,
            float(row["model_selection_score"]) if row.get("model_selection_score") else None,
            row.get("run_id", ""), task_type,
        )
