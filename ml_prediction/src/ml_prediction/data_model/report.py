import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


@dataclass
class Report:
    path: Path
    dataset: str

    fieldnames = (
        "timestamp",
        "dataset",
        "operation",
        "step",
        "partition",
        "rows",
        "model",
        "model_path",
        "model_id",
        "mae",
        "rmse",
        "r2",
        "details",
    )

    def __init__(self, path: Path, dataset: str, operation: str, model_path: Path | None = None) -> None:
        self.path = path
        self.dataset = dataset
        self.operation = operation
        self.model_path = model_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as report_file:
            csv.DictWriter(report_file, fieldnames=self.fieldnames).writeheader()

    def record(
            self,
            step: str,
            partition: str = "",
            rows: int | None = None,
            model_name: str = "",
            model_path: Path | None = None,
            metrics: RegressionMetrics | ClassificationMetrics | None = None,
            details: str = "",
    ) -> None:
        selected_model_path = model_path if isinstance(model_path, Path) else self.model_path
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataset": self.dataset,
            "operation": self.operation,
            "step": step,
            "partition": partition,
            "rows": rows if rows is not None else "",
            "model": model_name,
            "model_path": selected_model_path or "",
            "model_id": self.model_id(selected_model_path),
            "mae": getattr(metrics, "mean_absolute_error", ""),
            "rmse": getattr(metrics, "root_mean_squared_error", ""),
            "r2": getattr(metrics, "r2_score", ""),
            "details": details,
        }
        with self.path.open("a", newline="", encoding="utf-8") as report_file:
            csv.DictWriter(report_file, fieldnames=self.fieldnames).writerow(row)

    @staticmethod
    def model_id(model_path: Path | None) -> str:
        if not isinstance(model_path, Path) or not model_path.exists():
            return ""
        digest = hashlib.sha256()
        with model_path.open("rb") as model_file:
            for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
