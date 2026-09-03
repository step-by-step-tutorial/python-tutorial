from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


Metrics = RegressionMetrics | ClassificationMetrics


def metrics_to_dict(metrics: Metrics) -> dict[str, float]:
    return {key: float(value) for key, value in asdict(metrics).items()}


def metrics_from_dict(values: dict[str, Any], task_type: str) -> Metrics:
    metric_type = ClassificationMetrics if task_type == "classification" else RegressionMetrics
    return metric_type(**{key: float(value) for key, value in values.items()})


@dataclass(frozen=True)
class Experiment:
    fieldnames = (
        "experiment_id", "run_id", "timestamp", "dataset_name", "task_type", "model_type",
        "model_parameters", "model_selection_metric", "model_selection_score",
        "validation_metrics", "test_metrics", "model_path", "report_path",
    )

    experiment_id: str
    timestamp: datetime
    dataset_name: str
    model_type: str
    model_parameters: dict[str, Any]
    validation_metrics: Metrics
    test_metrics: Metrics
    model_path: Path
    report_path: Path | None
    model_selection_metric: str | None = None
    model_selection_score: float | None = None
    run_id: str = ""
    task_type: str = "regression"

    def to_row(self) -> dict[str, str | float]:
        task_type = self.task_type or (
            "classification" if isinstance(self.validation_metrics, ClassificationMetrics) else "regression"
        )
        return {
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "dataset_name": self.dataset_name,
            "task_type": task_type,
            "model_type": self.model_type,
            "model_parameters": json.dumps(self.model_parameters, sort_keys=True, separators=(",", ":")),
            "model_selection_metric": self.model_selection_metric or "",
            "model_selection_score": self.model_selection_score if self.model_selection_score is not None else "",
            "validation_metrics": json.dumps(metrics_to_dict(self.validation_metrics)),
            "test_metrics": json.dumps(metrics_to_dict(self.test_metrics)),
            "model_path": str(self.model_path),
            "report_path": str(self.report_path) if self.report_path is not None else "",
        }

    @staticmethod
    def from_row(row: dict[str, str]) -> "Experiment":
        task_type = row.get("task_type") or (
            "classification" if "f1_score" in row["validation_metrics"] else "regression"
        )
        return Experiment(
            experiment_id=row["experiment_id"],
            run_id=row.get("run_id", ""),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            dataset_name=row["dataset_name"],
            task_type=task_type,
            model_type=row["model_type"],
            model_parameters=json.loads(row["model_parameters"]),
            validation_metrics=metrics_from_dict(json.loads(row["validation_metrics"]), task_type),
            test_metrics=metrics_from_dict(json.loads(row["test_metrics"]), task_type),
            model_path=Path(row["model_path"]),
            report_path=Path(row["report_path"]) if row.get("report_path") else None,
            model_selection_metric=row.get("model_selection_metric") or None,
            model_selection_score=float(row["model_selection_score"]) if row.get("model_selection_score") else None,
        )


@dataclass(frozen=True)
class ReportEvent:
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


@dataclass(frozen=True)
class ModelMetadata:
    model_type: str
    model_parameters: dict[str, Any]
    target_column: str
    numeric_features: tuple[str, ...]
    boolean_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    training_timestamp: datetime
    validation_metrics: Metrics
    final_test_metrics: Metrics
    schema_version: str
    model_version: str
    dataset_name: str = "house"
    task_type: str = "regression"
    prediction_column: str = "predicted_total_price"
    run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["training_timestamp"] = self.training_timestamp.isoformat()
        value["validation_metrics"] = metrics_to_dict(self.validation_metrics)
        value["final_test_metrics"] = metrics_to_dict(self.final_test_metrics)
        return value
