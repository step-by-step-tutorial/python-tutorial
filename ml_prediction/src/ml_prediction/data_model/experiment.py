from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


@dataclass(frozen=True)
class Experiment:
    fieldnames = (
        "experiment_id",
        "timestamp",
        "dataset_name",
        "model_type",
        "model_parameters",
        "model_selection_metric",
        "model_selection_score",
        "validation_metrics",
        "test_metrics",
        "model_path",
        "report_path",
    )

    experiment_id: str
    timestamp: datetime
    dataset_name: str
    model_type: str
    model_parameters: dict[str, Any]
    validation_metrics: RegressionMetrics | ClassificationMetrics
    test_metrics: RegressionMetrics | ClassificationMetrics
    model_path: Path
    report_path: Path | None
    model_selection_metric: str | None = None
    model_selection_score: float | None = None

    def to_row(self) -> dict[str, str]:
        return {
            "experiment_id": self.experiment_id,
            "timestamp": self.timestamp.isoformat(),
            "dataset_name": self.dataset_name,
            "model_type": self.model_type,
            "model_parameters": json.dumps(self.model_parameters, sort_keys=True, separators=(",", ":")),
            "model_selection_metric": self.model_selection_metric or "",
            "model_selection_score": self.model_selection_score if self.model_selection_score is not None else "",
            "validation_metrics": json.dumps(asdict(self.validation_metrics)),
            "test_metrics": json.dumps(asdict(self.test_metrics)),
            "model_path": str(self.model_path),
            "report_path": str(self.report_path) if self.report_path is not None else "",
        }

    @staticmethod
    def from_row(row: dict[str, str]) -> "Experiment":
        return Experiment(
            experiment_id=row["experiment_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            dataset_name=row["dataset_name"],
            model_type=row["model_type"],
            model_parameters=json.loads(row["model_parameters"]),
            validation_metrics=RegressionMetrics(**json.loads(row["validation_metrics"])),
            test_metrics=RegressionMetrics(**json.loads(row["test_metrics"])),
            model_path=Path(row["model_path"]),
            report_path=Path(row["report_path"]) if row["report_path"] else None,
            model_selection_metric=row.get("model_selection_metric") or None,
            model_selection_score=(
                float(row["model_selection_score"])
                if row.get("model_selection_score")
                else None
            ),
        )
